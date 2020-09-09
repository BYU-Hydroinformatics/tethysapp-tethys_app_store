import os
import yaml
import time
import json
import importlib
import sys
import subprocess
import asyncio
import functools

from django.core.cache import cache
from django.core.cache import caches
from conda.cli.python_api import run_command as conda_run, Commands

from subprocess import call

from .app import Warehouse as app
from .helpers import *
from .resource_helpers import get_resource


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


def process_post_install_scripts(path):
    # Check if scripts directory exists
    scripts_dir = os.path.join(path, 'scripts')
    if os.path.exists(scripts_dir):
        logger.info("TODO: Process scripts dir.")
        # Currently only processing the pip install script, but need to add ability to process post scripts as well


def detect_app_dependencies(app_name, app_version, channel_layer):
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
    paths = list(filter(lambda x: app_name in x, tethysapp.__path__))

    if len(paths) < 1:
        print("Can't find the installed app location.")
        return
    # Check for any pre install script to install pip dependencies

    print(paths)
    # Check for a scripts directory
    # TODO : Complete pre install scripts here

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
        "returnMethod": "set_custom_settings",
        "jsHelperFunction": "processCustomSettings",
        "app_py_path": str(paths[0])
    }
    send_notification(get_data_json, channel_layer)

    return


def conda_install(app_metadata, app_version, channel_layer):

    start_time = time.time()
    send_notification(
        "Conda install may take a couple minutes to complete depending on how complicated the environment is. Please wait....", channel_layer)

    latest_version = app_metadata['metadata']['versions'][-1]
    if not app_version:
        app_version = latest_version

    # Try running the conda install as a subprocess to get more visibility into the running process
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, "scripts", "conda_install.sh")

    app_name = app_metadata['name'] + "=" + app_version
    install_command = [script_path, app_name, app_metadata['metadata']['channel']]

    # Running this sub process, in case the library isn't installed, triggers a restart.

    p = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.readline()
        print(output)
        if output == '':
            break
        if output:
            # Checkpoints for the output
            str_output = str(output.strip())
            logger.info(str_output)
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

    send_notification("Conda install completed in %.2f seconds." % (time.time() - start_time), channel_layer)


def begin_install(installData, channel_layer):

    app_workspace = app.get_app_workspace()
    resource = get_resource(installData["name"], app_workspace)

    send_notification("Starting installation of app: " + resource['name'], channel_layer)
    send_notification("Installing Version: " + installData["version"], channel_layer)

    try:
        app_path = conda_install(resource, installData["version"], channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while Installing Conda package. Please check logs for details", channel_layer)
        return

    try:
        detect_app_dependencies(resource['name'], installData["version"], channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while checking package for services", channel_layer)
        return
