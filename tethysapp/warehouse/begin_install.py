import os
import yaml
import time
import json
import importlib
import sys
import subprocess

from django.core.cache import cache
from conda.cli.python_api import run_command as conda_run, Commands
from asgiref.sync import async_to_sync
from subprocess import call

from .app import Warehouse as app
from .helpers import *


def check_all_present(string, substrings):
    result = True
    for substring in substrings:
        if substring not in string:
            result = False
            break
    return result


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

    call(['tethys', 'db', 'sync'])
    cache.clear()
    # clear_url_caches()
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
        for setting in custom_settings() or []:
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


async def detect_app_dependencies_async(app_name, app_version, channel_layer):
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
    paths = list(filter(lambda x: app_name in x, tethysapp.__path__))

    if len(paths) < 1:
        print("Can't find the installed app location.")
        return

    app_instance = get_app_instance_from_path(paths)
    custom_settings_json = []

    if getattr(app_instance, "custom_settings"):

        await channel_layer.group_send(
            "notifications",
            {
                "type": "install_notifications",
                "message": "Processing App's Custom Settings...."
            }
        )

        custom_settings = getattr(app_instance, "custom_settings")
        for setting in custom_settings() or []:
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
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )

    return


def conda_install(app_metadata, app_version, channel_layer):

    result = {
        'status': True,
        'msg': ""
    }
    send_notification(
        "Conda install may take a couple minutes to complete depending on how complicated the environment is. Please wait....", channel_layer)

    latest_version = app_metadata['metadata']['versions'][-1]
    if not app_version:
        app_version = latest_version

    # Try running the conda install as a subprocess to get more visibility into the running process
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, "conda_install.sh")

    app_name = app_metadata['name'] + "=" + app_version
    install_command = [script_path, app_name, app_metadata['metadata']['channel']]
    # Running this sub process, in case the library isn't installed, triggers a restart.
    p = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.readline()
        if output == '' and p.poll() is not None:
            break
        if output:
            # Checkpoints for the output
            str_output = str(output.strip())
            print(str_output)

            if(check_all_present(str_output, ['Collecting package metadata', 'done'])):
                send_notification("Package Metadata Collection: Done", channel_layer)
            if(check_all_present(str_output, ['Solving environment', 'done'])):
                send_notification("Solving Environment: Done", channel_layer)
            if(check_all_present(str_output, ['Verifying transaction', 'done'])):
                send_notification("Verifying Transaction: Done", channel_layer)
            if(check_all_present(str_output, ['All requested packages already installed.'])):
                send_notification("Application package is already installed in this conda environment.",
                                  channel_layer)
            if(check_all_present(str_output, ['Conda Install Complete'])):
                break
            if(check_all_present(str_output, ['Found conflicts!'])):
                send_notification("Conda install found conflicts."
                                  "Please try running the following command in your terminal's"
                                  "conda environment to attempt a manual installation : "
                                  "conda install -c " + app_metadata['metadata']['channel'] + " " + app_name,
                                  channel_layer)

    # run_command=["-c", app_metadata['metadata']['channel'], "-c", "conda-forge", app_name, '--json']
    # print(run_command)
    # [resp, err, code]=conda_run(Commands.INSTALL, *run_command, use_exception_handler=False, stdout=sys.stdout)
    # print(resp, err, code)
    # call(['tethys', 'db', 'sync'])
    # if code != 0:
    #     result['status']=False
    #     result['msg']='Warning: Conda installation ran into an error. Please try again or a manual install'
    # else:
    #     result['msg']='Conda Install Successful'
    #     send_notification("Conda install completed in %.2f seconds." % (time.time() - start_time), channel_layer)

    result['msg'] = 'Conda Install Successful'
    send_notification("Conda install completed", channel_layer)
    return result


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
