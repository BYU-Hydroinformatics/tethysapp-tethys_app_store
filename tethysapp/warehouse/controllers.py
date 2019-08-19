
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


from tethys_sdk.gizmos import (Button, MessageBox)

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

import yaml
import os
import xmltodict
import requests
import json
import asyncio
import threading

import xml.etree.ElementTree as ET


from .app import Warehouse as app
from .install_commands import *

# @TODO: Move these to settings that can be configured for the application

hs_client_id = 'EoHBKou1Sdcp69Y06zocwGA9BTKxAEQfEtt6EJ2i'
hs_client_secret = 'p31Osu284qCx2YJDf3tVIAkKTfoSPw0MccDPJ4p3MqfUm6lgPMS8tadKqjiLXqs\
moJixaPIeeYQkVOJkKhIfPlqArsPAp3h24eJvZnGxfwjmcNUREFSy5JUSePn6IOCM'

GROUP_ID = 120

ALL_RESOURCES = []


class notificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notifications", self.channel_name)
        print(f"Added {self.channel_name} channel to notifications")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        print(f"Removed {self.channel_name} channel from notifications")

    async def install_notifications(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message, }))
        print(f"Got message {event} at {self.channel_name}")


def parse_scimeta(url):
    r = requests.get(url)
    scimeta = xmltodict.parse(r.content)
    extended_metadata = scimeta['rdf:RDF']['rdf:Description'][0]['hsterms:extendedMetadata']
    final_metadata = {}
    for metadata in extended_metadata:
        metadata = metadata['rdf:Description']
        final_metadata[metadata['hsterms:key']] = metadata['hsterms:value']

    return final_metadata


def parse_resource(hs_resource):
    return {'title': hs_resource['resource_title'],
            'id': hs_resource['resource_id'],
            'description': hs_resource['abstract'],
            'date_created': hs_resource['date_created'],
            'date_last_updated': hs_resource['date_last_updated'],
            'metadata': parse_scimeta(hs_resource['science_metadata_url'])
            }


def fetch_resources():

    global ALL_RESOURCES

    # Commenting out the real hydroshare Fetch until the data model is created properly in the code
    # Once done here, reflect it on the actual resource
    # Doing this speeds up local dev

    resource_metadata = [{'title': 'Warehouse App 1 - Test',
                          'id': '1604fb12cced4f79bb6ceaf1a2c98090',
                          'description': 'Test Resource for Tethys App Warehouse.',
                          'date_created': '05-20-2019',
                          'date_last_updated': '07-17-2019',
                          'metadata': {'tethys-app': 'true',
                                       'test-metadata': '4443',
                                       'tethys-version': '2.0',
                                       'github-url': 'https://github.com/rfun/warehouse-test.git',
                                       'app-name': 'warehouse_test'}},
                         {'title': 'Warehouse App 2 - Test',
                          'id': 'b1bffcb8b48e447aa1cc240ac0824583',
                          'description': 'Test Resource for Tethys App Warehouse.',
                          'date_created': '05-21-2019', 'date_last_updated': '05-21-2019',
                          'metadata': {'tethys-app': 'true',
                                       'test-metadata': '4443',
                                       'tethys-version': '2.0',
                                       'github-url': 'https://github.com/BYU-Hydroinformatics/warehouse.git'}}]

    # auth = HydroShareAuthOAuth2(hs_client_id, hs_client_secret, username='rfun', password='bridgefour')
    # hs = HydroShare(auth=auth)
    # try:
    #     temp_resources = hs.resources(group=GROUP_ID)
    # except TokenExpiredError as e:
    #     hs = HydroShare(auth=auth)
    #     temp_resources = hs.resources(group=GROUP_ID)

    # resource_metadata = []

    # for resource in temp_resources:
    #     resource_metadata.append(parse_resource(resource))

    ALL_RESOURCES = resource_metadata


def get_resource(resource_id):

    # First see if resources are initialized
    if len(ALL_RESOURCES) == 0:
        fetch_resources()

    resource = [x for x in ALL_RESOURCES if x['id'] == resource_id]

    if len(resource) > 0:
        return resource[0]
    else:
        return None


def home(request):

    if len(ALL_RESOURCES) == 0:
        fetch_resources()

    message_box = MessageBox(name='notification',
                             title='Application Install Status',
                             dismiss_button='Nevermind',
                             affirmative_button='Refresh',
                             affirmative_attributes='onClick=window.location.href=window.location.href;')

    context = {'resources': ALL_RESOURCES, "install_message_box": message_box}
    return render(request, 'warehouse/home.html', context)


def install(request):

    app_id = request.GET.get('id')
    resource = get_resource(app_id)
    thread = threading.Thread(target=begin_install, args=(resource, get_channel_layer()))
    thread.start()
    return JsonResponse(resource)
