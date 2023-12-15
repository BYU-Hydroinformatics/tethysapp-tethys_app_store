from channels.generic.websocket import AsyncWebsocketConsumer
from .installation_handlers import logger, continueAfterInstall, restart_server, set_custom_settings,configure_services # noqa: F401
from .uninstall_handlers import uninstall_app # noqa: F401
from .git_install_handlers import get_log_file # noqa: F401
from .update_handlers import update_app # noqa: F401
from .resource_helpers import clear_cache # noqa: F401
from .submission_handlers import process_branch, validate_git_repo, pull_git_repo_all # noqa: F401
# called with threading.Thread
from .begin_install import begin_install  # noqa: F401
from tethys_sdk.routing import consumer
from tethys_sdk.workspaces import get_app_workspace
from asgiref.sync import sync_to_async

import json
import sys
import threading
from .app import AppStore as app


@consumer(
    name='install_notifications',
    url='install/notifications',
)
class notificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # breakpoint()
        await self.accept()
        await self.channel_layer.group_add("notifications", self.channel_name)
        logger.info(f"Added {self.channel_name} channel to notifications")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        logger.info(f"Removed {self.channel_name} channel from notifications")

    async def install_notifications(self, event):
        message = event['message']
        logger.info(f"print message {message} at {self.channel_name}")
        await self.send(text_data=json.dumps({'message': message, }))
        logger.info(f"Got message {event} at {self.channel_name}")
        
    async def receive(self, text_data):
        logger.info(f"Received message {text_data} at {self.channel_name}")
        # breakpoint()
        text_data_json = json.loads(text_data)
        function_name = text_data_json['type']
        module_name = sys.modules[__name__]
        args = [text_data_json['data'], self.channel_layer]
        app_workspace = await sync_to_async(get_app_workspace, thread_sensitive=True)(app)
        # app_workspace = get_app_workspace(app)
        if "type" in text_data_json:
            if text_data_json['type'] in ['begin_install', 'restart_server', 'get_log_file', 'pull_git_repo_all',
                                          'update_app', 'uninstall_app']:
                args.append(app_workspace)
            thread = threading.Thread(target=getattr(module_name, function_name), args=args)
            thread.start()
        else:
            logger.info("Can't redirect incoming message.")
