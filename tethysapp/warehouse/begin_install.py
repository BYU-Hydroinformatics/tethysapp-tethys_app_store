import os
import yaml
import time
import json
import importlib

from conda.cli.python_api import run_command as conda_run, Commands
from asgiref.sync import async_to_sync
from subprocess import call

from .app import Warehouse as app
from .installation_handlers import get_app_instance_from_path


def handle_property_not_present(prop):
    # TODO: Generate an error message that metadata is incorrect for this application
    pass


def send_notification(msg, channel_layer):
    async_to_sync(channel_layer.group_send)(
        "notifications", {
            "type": "install_notifications",
            "message": msg
        }
    )


def detect_app_dependencies(install_metadata, app_version, channel_layer):
    """
    Method goes through the app.py and determines the following:
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

    # paths = list()
    paths = list(filter(lambda x: install_metadata['name'] in x, tethysapp.__path__))

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

    return


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


def begin_install(install_metadata, app_version, channel_layer):
    send_notification("Starting installation of app: " + install_metadata['name'], channel_layer)
    send_notification("Installing Version: " + app_version, channel_layer)

    # try:
    #     app_path = conda_install(install_metadata, app_version, channel_layer)
    # except Exception as e:
    #     print(e)
    #     send_notification("Error while Installing Conda package. Please check logs for details", channel_layer)
    #     return

    try:
        detect_app_dependencies(install_metadata, app_version, channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while checking package for services", channel_layer)
        return
