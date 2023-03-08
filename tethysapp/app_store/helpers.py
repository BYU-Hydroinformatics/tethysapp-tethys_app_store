import pkgutil
import inspect
import sys
import importlib
import logging
import json
import shutil
import os
import re

from tethys_apps.base import TethysAppBase
from django.conf import settings
from django.urls.base import clear_url_caches
from django.core.cache import cache

from asgiref.sync import async_to_sync
from conda.cli.python_api import run_command as conda_run, Commands
from string import Template
from subprocess import run

logger = logging.getLogger('tethys.apps.app_store')
# Ensure that this logger is putting everything out.
# @TODO: Change this back to the default later
logger.setLevel(logging.INFO)

CACHE_KEY = "warehouse_github_app_resources"


def get_override_key():
    try:
        return settings.GITHUB_OVERRIDE_VALUE
    except AttributeError:
        # Setting not defined.
        return None


def check_all_present(string, substrings):
    result = True
    for substring in substrings:
        if substring not in string:
            result = False
            break
    return result


def run_process(args):
    result = run(args, capture_output=True)
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)


def check_if_app_installed(app_name):
    return_obj = {}
    try:
        [resp, err, code] = conda_run(
            Commands.LIST, ["-f",  "--json", app_name])
        if code != 0:
            # In here maybe we just try re running the install
            logger.error(
                "ERROR: Couldn't get list of installed apps to verify if the conda install was successfull")
        else:
            conda_search_result = json.loads(resp)
            if len(conda_search_result) > 0:
                # return conda_search_result[0]["version"]
                return_obj['isInstalled'] = True
                return_obj['channel'] = conda_search_result[0]["channel"]
                return_obj['version'] = conda_search_result[0]["version"]
                return return_obj
            
            else:
                return_obj['isInstalled'] = False
                return return_obj
    except RuntimeError:
        err_string = str(err)
        if "Path not found" in err_string and "tethysapp_warehouse" in err_string:
            # Old instance of warehouse files present. Need to cleanup
            err_path = err_string.split(": ")[1]
            if "EGG-INFO" in err_path:
                err_path = err_path.replace("EGG-INFO", '')

            if os.path.exists(err_path):
                shutil.rmtree(err_path)

            logger.info("Cleaning up: " + err_path)
        return check_if_app_installed(app_name)



def add_if_exists(a, b, keys):
    if not a:
        return b
    for key in keys:
        if key in a:
            b[key] = a[key]
    return b

def add_if_exists_keys(a, final_a, keys,channel,label):
    if not a:
        return final_a
    for key in keys:
        if key not in final_a:
            final_a[key] = {}
            if channel not in final_a[key]:
                final_a[key][channel] = {}
                if label not in final_a[key][channel] and key in a:
                    final_a[key][channel][label] = a[key]

    return final_a
    

def get_app_instance_from_path(paths):
    app_instance = None
    for _, modname, ispkg in pkgutil.iter_modules(paths):
        if ispkg:
            app_module = __import__('tethysapp.{}'.format(
                modname) + ".app", fromlist=[''])
            for name, obj in inspect.getmembers(app_module):
                # Retrieve the members of the app_module and iterate through
                # them to find the the class that inherits from AppBase.
                try:
                    # issubclass() will fail if obj is not a class
                    if (issubclass(obj, TethysAppBase)) and (obj is not TethysAppBase):
                        # Assign a handle to the class
                        AppClass = getattr(app_module, name)
                        # Instantiate app
                        app_instance = AppClass()
                        app_instance.sync_with_tethys_db()
                        # We found the app class so we're done
                        break
                except TypeError:
                    continue
    return app_instance


def reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        importlib.reload(sys.modules[urlconf])
    clear_url_caches()


def send_notif(msg, channel_layer):
    return channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": msg
        }
    )


def send_notification(msg, channel_layer):
    async_to_sync(channel_layer.group_send)(
        "notifications", {
            "type": "install_notifications",
            "message": msg
        }
    )


# Template Generator

def apply_template(template_location, data, output_location):
    filein = open(template_location)
    src = Template(filein.read())
    result = src.substitute(data)
    with open(output_location, "w") as f:
        f.write(result)


def parse_setup_py(file_location):
    params = {}
    found_setup = False
    with open(file_location, "r") as f:
        for line in f.readlines():
            if ("setup(" in line):
                found_setup = True
                continue
            if found_setup:
                if (")" in line):
                    found_setup = False
                    break
                else:
                    parts = line.split("=")
                    if len(parts) < 2:
                        continue
                    value = parts[1].strip()
                    if(value[-1] == ","):
                        value = value[:-1]
                    if(value[0] == "'" or value[0] == '"'):
                        value = value[1:]
                    if(value[-1] == "'" or value[-1] == '"'):
                        value = value[:-1]
                    params[parts[0].strip()] = value
    return params

# Get apps that might have been installed via GitHub install process


def find_string_in_line(line):
    # try singleQuotes First
    matches = re.findall("'([^']*)'", line)
    if len(matches) > 0:
        return matches[0]
    else:
        # try double quotes
        matches = re.findall('"([^"]*)"', line)
        if len(matches) > 0:
            return matches[0]


def get_github_install_metadata(app_workspace):

    if (cache.get(CACHE_KEY) is None):
        logger.info("GitHub Apps list cache miss")
        workspace_directory = app_workspace.path
        workspace_apps_path = os.path.join(
            workspace_directory, 'apps', 'installed')
        if(not os.path.exists(workspace_apps_path)):
            cache.set(CACHE_KEY, [])
            return []

        possible_apps = [f.path for f in os.scandir(
            workspace_apps_path) if f.is_dir()]
        github_installed_apps_list = []
        for possible_app in possible_apps:
            installed_app = {
                'name': '',
                'installed': True,
                'metadata':
                {
                    'channel': 'tethysapp',
                    'license': 'BSD 3-Clause License',
                },
                'installedVersion': '',
                'path': possible_app
            }
            setup_path = os.path.join(possible_app, 'setup.py')
            with open(setup_path, 'rt') as myfile:
                for myline in myfile:
                    if 'app_package' in myline and 'find_resource_files' not in myline and 'release_package' not in myline: # noqa e501
                        installed_app["name"] = find_string_in_line(myline)
                        continue
                    if 'version' in myline:
                        installed_app["installedVersion"] = find_string_in_line(
                            myline)
                        continue
                    if 'description' in myline:
                        installed_app["metadata"]["description"] = find_string_in_line(
                            myline)
                        continue
                    if 'author' in myline:
                        installed_app["author"] = find_string_in_line(myline)
                        continue
                    if 'description' in myline:
                        installed_app["installedVersion"] = find_string_in_line(
                            myline)
                        continue
                    if 'url' in myline:
                        installed_app["dev_url"] = find_string_in_line(
                            myline)
                        continue
            github_installed_apps_list.append(installed_app)
        cache.set(CACHE_KEY, github_installed_apps_list)
        return github_installed_apps_list
    else:
        return cache.get(CACHE_KEY)


def check_github_install(app_name, app_workspace):
    possible_apps = get_github_install_metadata(app_workspace)
    print(possible_apps)


def get_github_installed_apps():

    # print(possible_apps)

    return ""
