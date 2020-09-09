from conda.cli.python_api import run_command as conda_run, Commands
from tethys_cli.cli_helpers import get_manage_path
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

    send_uninstall_messages('Starting Uninstall. Please wait...', channel_layer)

    manage_path = get_manage_path({})
    item_name = data['name']
    process = ['python', manage_path, 'tethys_app_uninstall', item_name]
    process.append('-f')

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass

    send_uninstall_messages('Tethys App Uninstalled. Running Conda Cleanup...', channel_layer)

    [resp, err, code] = conda_run(Commands.REMOVE, ["-c", "tethysplatform", "--override-channels", data['name']])

    print(resp, err, code)
    send_uninstall_messages('Uninstall completed. Restarting server...', channel_layer)
