from channels.generic.websocket import AsyncWebsocketConsumer
from .installation_handlers import *
from .submission_handlers import *
from .begin_install import begin_install
from .uninstall_handlers import *
from .resource_helpers import clear_cache

import json
import sys

import threading


class notificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notifications", self.channel_name)
        logger.info(f"Added {self.channel_name} channel to notifications")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        logger.info(f"Removed {self.channel_name} channel from notifications")

    async def install_notifications(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message, }))
        # logger.info(f"Got message {event} at {self.channel_name}")

    async def receive(self, text_data):
        # logger.info(f"Received message {text_data} at {self.channel_name}")
        text_data_json = json.loads(text_data)
        if "type" in text_data_json:
            thread = threading.Thread(target=getattr(sys.modules[__name__], text_data_json['type']),
                                      args=(text_data_json['data'], self.channel_layer)
                                      )
            thread.start()
        else:
            logger.info("Can't redirect incoming message.")
