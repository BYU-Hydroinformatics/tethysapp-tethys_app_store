import os
import time
import importlib
import subprocess

from django.core.cache import cache

from subprocess import call

from .helpers import check_all_present, get_app_instance_from_path, logger, send_notification
from .resource_helpers import get_resource, get_resource_new


def handle_property_not_present(prop):
    # TODO: Generate an error message that metadata is incorrect for this application
    pass


def process_post_install_scripts(path):
    # Check if scripts directory exists
    scripts_dir = os.path.join(path, 'scripts')
    if os.path.exists(scripts_dir):
        logger.info("TODO: Process scripts dir.")
        # Currently only processing the pip install script, but need to add ability to process post scripts as well


def detect_app_dependencies(app_name, channel_layer, notification_method=send_notification):
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
    # store_pkg = importlib.import_module(app_channel)

    call(['tethys', 'db', 'sync'])
    cache.clear()
    # clear_url_caches()
    # After install we need to update the sys.path variable so we can see the new apps that are installed.
    # We need to do a reload here of the sys.path and then reload the tethysapp
    # https://stackoverflow.com/questions/25384922/how-to-refresh-sys-path
    import site
    importlib.reload(site)
    importlib.reload(tethysapp)
    # importlib.reload(store_pkg)

    # paths = list()
    # paths = list(filter(lambda x: app_name in x, store_pkg.__path__))
    # breakpoint()
    paths = list(filter(lambda x: app_name in x, tethysapp.__path__))


    if len(paths) < 1:
        logger.error("Can't find the installed app location.")
        return

    # Check for any pre install script to install pip dependencies

    app_folders = next(os.walk(paths[0]))[1]
    app_scripts_path = os.path.join(paths[0], app_folders[0], 'scripts')
    pip_install_script_path = os.path.join(app_scripts_path, 'install_pip.sh')

    if os.path.exists(pip_install_script_path):
        logger.info("PIP dependencies found. Running Pip install script")
        # breakpoint()
        notification_method("Running PIP install....", channel_layer)
        p = subprocess.Popen(['sh', pip_install_script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = p.stdout.readline()
            if output == '':
                break
            if output:
                # Checkpoints for the output
                str_output = str(output.strip())
                logger.info(str_output)
                if(check_all_present(str_output, ['PIP Install Complete'])):
                    break

        notification_method("PIP install completed", channel_layer)

    # @TODO: Add support for post installation scripts as well.

    app_instance = get_app_instance_from_path(paths)
    custom_settings_json = []

    if getattr(app_instance, "custom_settings"):
        notification_method("Processing App's Custom Settings....", channel_layer)
        custom_settings = getattr(app_instance, "custom_settings")
        for setting in custom_settings() or []:
            setting = {"name": getattr(setting, "name"),
                       "description": getattr(setting, "description"),
                       "default": str(getattr(setting, "default")),
                       }
            custom_settings_json.append(setting)

    get_data_json = {
        "data": custom_settings_json,
        "returnMethod": "set_custom_settings",
        "jsHelperFunction": "processCustomSettings",
        "app_py_path": str(paths[0])
    }
    notification_method(get_data_json, channel_layer)

    return


def conda_install(app_metadata, app_channel,app_label,app_version, channel_layer):

    start_time = time.time()
    send_notification("Mamba install may take a couple minutes to complete depending on how complicated the "
                      "environment is. Please wait....", channel_layer)

    latest_version = app_metadata['latestVersion'][app_channel][app_label]
    if not app_version:
        app_version = latest_version

    # Running the conda install as a subprocess to get more visibility into the running process
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # breakpoint()
    script_path = os.path.join(dir_path, "scripts", "conda_install.sh")

    app_name = app_metadata['name'] + "=" + app_version

    label_channel = f'{app_channel}'
    
    if app_label != 'main':
        label_channel = f'{app_channel}/label/{app_label}'

    install_command = [script_path, app_name, label_channel]

    # Running this sub process, in case the library isn't installed, triggers a restart.

    p = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        output = p.stdout.readline()
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
            if(check_all_present(str_output, ['Mamba Install Complete'])):
                break
            if(check_all_present(str_output, ['Found conflicts!'])):
                send_notification("Mamba install found conflicts."
                                  "Please try running the following command in your terminal's"
                                  "conda environment to attempt a manual installation : "
                                  "mamba install -c " + label_channel + " " + app_name,
                                  channel_layer)

    send_notification("Mamba install completed in %.2f seconds." % (time.time() - start_time), channel_layer)


def begin_install(installData, channel_layer, app_workspace):

    # resource = get_resource(installData["name"], app_workspace)
    # breakpoint()

    resource = get_resource_new(installData["name"],installData['channel'],installData['label'], app_workspace)
    
    send_notification("Starting installation of app: " + resource['name'] + " from store "+ installData['channel'] + " with label "+ installData['label'] , channel_layer)
    send_notification("Installing Version: " + installData["version"], channel_layer)


    try:
        conda_install(resource,installData['channel'],installData['label'], installData["version"], channel_layer)
    except Exception as e:
        logger.error("Error while running conda install")
        logger.error(e)
        send_notification("Error while Installing Conda package. Please check logs for details", channel_layer)
        return

    try:
        detect_app_dependencies(resource['name'], channel_layer)
    except Exception as e:
        logger.error(e)
        send_notification("Error while checking package for services", channel_layer)
        return
