from conda.cli.python_api import run_command as conda_run, Commands
from tethys_cli.cli_helpers import get_manage_path
from tethys_apps.exceptions import TethysAppSettingNotAssigned

import subprocess

from .helpers import logger, send_notification
from .installation_handlers import restart_server


def send_uninstall_messages(msg, channel_layer):
    data_json = {
        "target": 'uninstallNotices',
        "message": msg
    }
    send_notification(data_json, channel_layer)


def uninstall_app(data, channel_layer):

    manage_path = get_manage_path({})
    app_name = data['name']

    send_uninstall_messages('Starting Uninstall. Please wait...', channel_layer)

    try:
        # Check if application had provisioned any Persistent stores and clear them out
        from tethys_apps.models import TethysApp
        target_app = TethysApp.objects.filter(package=app_name)[0]
        ps_db_settings = target_app.persistent_store_database_settings

        if len(ps_db_settings):
            for setting in ps_db_settings:
                # If there is a db for this PS, drop it
                try:
                    if setting.persistent_store_database_exists():
                        logger.info("Droping Database for persistent store setting: " + str(setting))
                        setting.drop_persistent_store_database()
                except TethysAppSettingNotAssigned:
                    pass

        else:
            logger.info("No Persistent store services found for: " + app_name)
    except IndexError:
        # Couldn't find the target application
        logger.info("Couldn't find the target application for removal of databases. Continuing clean up")

    process = ['python', manage_path, 'tethys_app_uninstall', app_name]
    process.append('-f')

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass

    send_uninstall_messages('Tethys App Uninstalled. Running Conda Cleanup...', channel_layer)

    [resp, err, code] = conda_run(Commands.REMOVE, ["--force", "-c", "tethysplatform",
                                                    "--override-channels", data['name']])

    logger.info(resp)
    if err:
        logger.error(err)

    send_uninstall_messages('Uninstall completed. Restarting server...', channel_layer)
