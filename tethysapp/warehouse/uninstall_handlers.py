
from tethys_cli.cli_helpers import get_manage_path
import subprocess

from .helpers import logger, send_notification


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

    print("UNINSTALL DONE? ")
