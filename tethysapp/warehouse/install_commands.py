import os
import yaml
import time
import json
import importlib
import pkgutil
import inspect

from subprocess import call, STDOUT
from conda.cli.python_api import run_command as conda_run, Commands
from asgiref.sync import async_to_sync
from pathlib import Path
from argparse import Namespace
from subprocess import (call)

from distutils.sysconfig import get_python_lib
from django.core.exceptions import ObjectDoesNotExist
from tethys_apps.base import TethysAppBase
from tethys_apps.models import CustomSetting, TethysApp
from tethys_apps.utilities import (get_app_settings, link_service_to_app_setting)
from tethys_cli.install_commands import (get_service_type_from_setting, get_setting_type_from_setting)
from tethys_cli.services_commands import services_list_command

from .app import Warehouse as app


async def configureServices(services_data, channel_layer):
    print(services_data)

    try:
        link_service_to_app_setting(services_data['service_type'],
                                    services_data['service_id'],
                                    services_data['app_name'],
                                    services_data['setting_type'],
                                    services_data['service_name'])
    except Exception as e:
        print(e)
        print("Error while linking service")
        return

    get_data_json = {
        "data": {"serviceName": services_data['service_name']},
        "jsHelperFunction": "serviceConfigComplete"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )


async def setCustomSettings(custom_settings_data, channel_layer):

    current_app = get_app_instance_from_path([custom_settings_data['app_py_path']])

    if "skip" in custom_settings_data:
        if(custom_settings_data["skip"]):
            print("Skip/NoneFound option called.")

            msg = "Custom Setting Configuration Skipped"
            if "noneFound" in custom_settings_data:
                if custom_settings_data["noneFound"]:
                    msg = "No Custom Settings Found to process."

            await channel_layer.group_send(
                "notifications",
                {
                    "type": "install_notifications",
                    "message": msg
                }
            )
            await process_settings(current_app, custom_settings_data['app_py_path'], channel_layer)
            return

    current_app_name = getattr(current_app, "name")
    custom_settings = getattr(current_app, "custom_settings")

    try:
        current_app_tethysapp_instance = TethysApp.objects.get(name=current_app_name)
    except ObjectDoesNotExist:
        print("Couldn't find app instance to get the ID to connect the settings to")
        await channel_layer.group_send(
            "notifications",
            {
                "type": "install_notifications",
                "message": "Error Setting up custom settings. Check logs for more details"
            }
        )
        return

    for setting in custom_settings():
        setting_name = getattr(setting, "name")
        actual_setting = CustomSetting.objects.get(name=setting_name, tethys_app=current_app_tethysapp_instance.id)
        if(setting_name in custom_settings_data['settings']):
            actual_setting.value = custom_settings_data['settings'][setting_name]
            actual_setting.clean()
            actual_setting.save()

    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": "Custom Settings configured."
        }
    )
    get_data_json = {
        "data": {},
        "jsHelperFunction": "customSettingConfigComplete"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )
    await process_settings(current_app, custom_settings_data['app_py_path'], channel_layer)


def send_notification(msg, channel_layer):
    async_to_sync(channel_layer.group_send)(
        "notifications", {
            "type": "install_notifications",
            "message": msg
        }
    )


def get_app_instance_from_path(paths):
    app_instance = None
    for _, modname, ispkg in pkgutil.iter_modules(paths):
        if ispkg:
            app_module = __import__('tethysapp.{}'.format(modname) + ".app", fromlist=[''])
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


def get_service_options(service_type):
    # # List existing services
    args = Namespace()

    for conf in ['spatial', 'persistent', 'wps', 'dataset']:
        setattr(args, conf, False)

    setattr(args, service_type, True)

    existing_services_list = services_list_command(args)[0]
    existing_services = []

    if(len(existing_services_list)):
        for service in existing_services_list:
            existing_services.append({
                "name": service.name,
                "id": service.id
            })
    return existing_services


async def process_settings(app_instance, app_py_path, channel_layer):
    app_settings = get_app_settings(app_instance.package)

    # In the case the app isn't installed, has no settings, or it is an extension,
    # skip configuring services/settings
    if not app_settings:
        await channel_layer.group_send(
            "notifications",
            {
                "type": "install_notifications",
                "message": "No Services found to configure."
            }
        )

        return
    unlinked_settings = app_settings['unlinked_settings']

    services = []

    for setting in unlinked_settings:
        service_type = get_service_type_from_setting(setting)
        newSetting = {
            "name": setting.name,
            "required": setting.required,
            "description": setting.description,
            "service_type": service_type,
            "setting_type": get_setting_type_from_setting(setting),
            "options": get_service_options(service_type)
        }
        services.append(newSetting)

    get_data_json = {
        "data": services,
        "returnMethod": "configureServices",
        "jsHelperFunction": "processServices",
        "app_py_path": app_py_path,
        "current_app_name": app_instance.package
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )


def detect_app_dependencies(install_metadata, app_version, channel_layer):
    """
    Method goes through the app.xml and determines the following:
    1.) Any services required
    2.) Thredds?
    3.) Geoserver Requirement?
    4.) Custom Settings required for installation?
    """

    # Get Conda Packages location

    # Tried using conda_prefix from env as well as conda_info but both of them are not reliable
    # Best method is to import the module and try and get the location from that path
    # @TODO : Ensure that this works through multiple runs
    import tethysapp

    # After install we need to update the sys.path variable so we can see the new apps that are installed.
    # We need to do a reload here of the sys.path and then reload the the tethysapp
    # https://stackoverflow.com/questions/25384922/how-to-refresh-sys-path
    import site
    importlib.reload(site)
    importlib.reload(tethysapp)

    paths = list(tethysapp.__path__)
    print("Current paths", paths)
    paths = list(filter(lambda x: install_metadata['name'] in x, paths))

    if len(paths) < 1:
        print("Can't find the installed app location.")
        return

    app_instance = get_app_instance_from_path(paths)
    custom_settings_json = []

    if getattr(app_instance, "custom_settings"):
        send_notification("Processing App's Custom Settings....", channel_layer)
        custom_settings = getattr(app_instance, "custom_settings")
        for setting in custom_settings():
            setting = {"name": getattr(setting, "name"),
                       "description": getattr(setting, "description"),
                       "default": getattr(setting, "default"),
                       }
            custom_settings_json.append(setting)

    get_data_json = {
        "data": custom_settings_json,
        "returnMethod": "setCustomSettings",
        "jsHelperFunction": "processCustomSettings",
        "app_py_path": str(paths[0])
    }
    send_notification(get_data_json, channel_layer)

    # else:
    #     get_data_json = {
    #         "returnMethod": "setCustomSettings",
    #         "jsHelperFunction": "processCustomSettings",
    #         "app_py_path": str(paths[0])
    #     }
    #     send_notification(get_data_json, channel_layer)
    # process_settings(app_instance, str(paths[0]), channel_layer)
    # send_notification("No Custom Settings found in the App to Process.", channel_layer)

    # # First let's try the environment variables
    # if "CONDA_PREFIX" in os.environ:
    #     conda_pkgs_location = os.path.join(os.environ["CONDA_PREFIX"], "pkgs")
    # else:
    #     # Try and get it from conda info
    #     (conda_info_result, err, code) = conda_run(Commands.INFO, ["--json"])
    #     # print(conda_info_result, err, code)
    #     try:
    #         conda_info_result = json.loads(conda_info_result)
    #     except Exception as e:
    #         print("Error while parsing info result")
    #         print(conda_info_result)
    #         print(e)
    #         # Need to throw an error here
    #         return

    #     conda_pkgs_location = conda_info_result['pkgs_dirs'][0]

    # download_url = install_metadata['metadata']['versionURLs'][install_metadata['metadata']
    #                                                            ['versions'].index(app_version)]
    # downloaded_file_name = '.'.join(download_url.split("/")[-1].split('.')[:-2])
    # repo_location = os.path.join(conda_pkgs_location, downloaded_file_name)
    # print(repo_location)

    # print(dir(current_app))
    # object_methods = [method_name for method_name in dir(current_app)
    #                   if callable(getattr(current_app, method_name)) and "TethysAppBase" not in str(getattr(current_app, method_name))]

    # Object methods only contains items in the app.py now.

    # if 'custom_settings' in object_methods:
    #     process_custom_settings(getattr(current_app, 'custom_settings'))

    return


def handle_property_not_present(prop):
    # TODO: Generate an error message that metadata is incorrect for this application
    pass


def get_repo(app_name, repo_link, channel_layer, branch="master", ):
    # TODO :  What Happens when git pull fails or one of the other operations in here?
    send_notification("Pulling GIT Repo", channel_layer)

    dir_path = os.path.join(app.get_app_workspace().path, 'apps', app_name)
    if os.path.isdir(dir_path):
        print("Path already exists, could be an update operation?. Skipping Git checkout, just do a pull")
        # repo = git.Repo(dir_path)
        # o = repo.remotes.origin
        # o.pull()
    else:
        os.mkdir(dir_path)

        repo = git.Repo.init(dir_path)
        origin = repo.create_remote('origin', repo_link)
        origin.fetch()
        repo.git.checkout(branch)

        for root, dirs, files in os.walk(dir_path):
            for momo in dirs:
                os.chmod(os.path.join(root, momo), 0o755)
            for momo in files:
                os.chmod(os.path.join(root, momo), 0o755)

    send_notification("GIT Repo Pull Complete", channel_layer)

    return dir_path


# Function to check if the downloaded repo contains valid install yaml files.

def validate_app(path):
    validation = {'valid': True}
    # Check if Install.yml or install.yaml is present
    install_path = os.path.join(path, 'install')
    if not (os.path.exists(install_path + '.yml') or os.path.exists(install_path + '.yaml')):
        validation['valid'] = False
        return validation
    else:
        if os.path.exists(install_path + '.yml'):
            validation['path'] = install_path + '.yml'
        else:
            validation['path'] = install_path + '.yaml'

    return validation


def conda_install(app_metadata, app_version, channel_layer):

    result = {
        'status': True,
        'msg': ""
    }
    send_notification(
        "Conda install may take a couple minutes to complete depending on how complicated the environment is. Please wait....", channel_layer)

    start_time = time.time()
    latest_version = app_metadata['metadata']['versions'][-1]
    if not app_version:
        app_version = latest_version

    app_name = app_metadata['name'] + "=" + app_version
    run_command = ["-c", app_metadata['metadata']['channel'], "-c", "conda-forge", app_name, '--json']
    # print(run_command)
    [resp, err, code] = conda_run(Commands.INSTALL, *run_command, use_exception_handler=False)
    call(['tethys', 'db', 'sync'])
    if code != 0:
        result['status'] = False
        result['msg'] = 'Warning: Conda installation ran into an error. Please try again or a manual install'
    else:
        result['msg'] = 'Conda Install Successful'
        send_notification("Conda install completed in %.2f seconds." % (time.time() - start_time), channel_layer)

    return result


def install_conda_deps(conda_config):
    result = {
        'status': True,
        'msg': ""
    }
    install_args = []
    if "channels" in conda_config and conda_config['channels'] and len(conda_config['channels']) > 0:
        channels = conda_config['channels']
    else:
        channels = ['conda-forge']

    # Install all Dependencies

    if "dependencies" in conda_config and conda_config['dependencies'] and len(conda_config['dependencies']) > 0:
        dependencies = conda_config['dependencies']
        print('Installing Conda Dependencies.....')
        run_command = ["-c", *channels, *dependencies]
        [resp, err, code] = conda_run(Commands.INSTALL, *run_command, use_exception_handler=False)
        if code != 0:
            result['status'] = False
            result['msg'] = 'Warning: Dependencies installation ran into an error. Please try again or a manual install'
        else:
            result['msg'] = 'Conda Install Successful'

    return result


def install_pip_deps(pip_config):
    if pip_config and len(pip_config) > 0:
        from pip._internal import main as pip
        for pip_req in pip_config:
            pip(['install', '--user', pip_req])
    return {
        'status': True,
        'msg': "Pip Dependencies Installed"
    }


def run_install(install_path, channel_layer):

    call(['tethys', 'db', 'sync'])
    send_notification("Python application setup complete", channel_layer)

    return {
        'status': True,
        'msg': 'Install App and Deps Successful',
        'conda_result': conda_install_result,
        'pip_result': pip_install_result
    }


def begin_install(install_metadata, app_version, channel_layer):
    send_notification("Starting installation of app: " + install_metadata['name'], channel_layer)
    send_notification("Installing Version: " + app_version, channel_layer)

    try:
        app_path = conda_install(install_metadata, app_version, channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while Installing Conda package. Please check logs for details", channel_layer)
        return

    try:
        detect_app_dependencies(install_metadata, app_version, channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while checking package for services", channel_layer)
        return
    # try:
    #     install_status = run_install(validation['path'], channel_layer)
    # except Exception as e:
    #     send_notification("Install ran into an error. Please check logs for details", channel_layer)
    #     return

    # if install_status['status']:
    #     send_notification("install_complete", channel_layer)
