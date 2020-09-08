import pkgutil
import inspect
import sys
import importlib
import logging
import json

from tethys_apps.base import TethysAppBase
from django.conf import settings
from django.urls.base import clear_url_caches
from asgiref.sync import async_to_sync
from conda.cli.python_api import run_command as conda_run, Commands
from string import Template

logger = logging.getLogger(f'tethys.apps.warehouse')
# Ensure that this logger is putting everything out.
# @TODO: Change this back to the default later
logger.setLevel(logging.INFO)


def check_if_app_installed(app_name):
    [resp, err, code] = conda_run(Commands.LIST, [app_name, "--json"])
    # logger.info(resp, err, code)
    if code != 0:
        # In here maybe we just try re running the install
        logger.error("ERROR: Couldn't get list of installed apps to verify if the conda install was successfull")
    else:
        conda_search_result = json.loads(resp)
        if len(conda_search_result) > 0:
            return conda_search_result[0]["version"]
        else:
            return False


def add_if_exists(a, b, keys):
    if not a:
        return b
    for key in keys:
        if key in a:
            b[key] = a[key]
    return b


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
