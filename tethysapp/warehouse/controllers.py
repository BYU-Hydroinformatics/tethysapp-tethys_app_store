from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from tethys_sdk.gizmos import (Button, MessageBox)

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from conda.cli.python_api import Commands, run_command

import yaml
import os
import xmltodict
import requests
import json
import asyncio
import threading
import re
import conda.cli.python_api
import sys
from packaging import version
import xml.etree.ElementTree as ET

from .app import Warehouse as app
from .install_commands import *

# @TODO: Move these to settings that can be configured for the application

hs_client_id = 'EoHBKou1Sdcp69Y06zocwGA9BTKxAEQfEtt6EJ2i'
hs_client_secret = 'p31Osu284qCx2YJDf3tVIAkKTfoSPw0MccDPJ4p3MqfUm6lgPMS8tadKqjiLXqs\
moJixaPIeeYQkVOJkKhIfPlqArsPAp3h24eJvZnGxfwjmcNUREFSy5JUSePn6IOCM'

GROUP_ID = 120

ALL_RESOURCES = []

CHANNEL_NAME = 'rfun'


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

    async def receive(self, text_data):
        # print(f"Received message {text_data} at {self.channel_name}")
        text_data_json = json.loads(text_data)
        if "type" in text_data_json:
            await getattr(sys.modules[__name__], text_data_json['type'])(text_data_json['data'], self.channel_layer)
        else:
            print("Can't redirect incoming message.")


def parse_scimeta(url):
    r = requests.get(url)
    scimeta = xmltodict.parse(r.content)
    extended_metadata = scimeta['rdf:RDF']['rdf:Description'][0]['hsterms:extendedMetadata']
    final_metadata = {}
    final_metadata['app_tags'] = list(map(lambda x: re.sub(r"\s+", '-', x),
                                          scimeta['rdf:RDF']['rdf:Description'][0]['dc:subject']))
    for metadata in extended_metadata:
        metadata = metadata['rdf:Description']
        final_metadata[metadata['hsterms:key']] = metadata['hsterms:value']
    return final_metadata


def parse_resource(hs_resource):
    print(hs_resource['science_metadata_url'])
    return {'title': hs_resource['resource_title'],
            'id': hs_resource['resource_id'],
            'description': hs_resource['abstract'],
            'date_created': hs_resource['date_created'],
            'date_last_updated': hs_resource['date_last_updated'],
            'metadata': parse_scimeta(hs_resource['science_metadata_url'])
            }


def fetch_resources():
    global ALL_RESOURCES

    # Fields that are required
    # resource_metadata_template = {
    #     'name': "App Name",
    #     'description': "Description",
    #     'metadata': {
    #         'app_tags': ['App-Category-1'],
    #         'icon': "Icon location",
    #         'versions':['0.0.0']
    #     }
    # }

    # Look for packages:
    # conda search - c geoglows - -override-channels - i
    (conda_search_result, err, code) = run_command(Commands.SEARCH,
                                                   ["-c", CHANNEL_NAME, "--override-channels", "-i", "--json"])
    conda_search_result = json.loads(conda_search_result)

    resource_metadata = []
    for conda_package in conda_search_result:
        newPackage = {
            'name': conda_package,
            'metadata': {
                'versions': [],
                'versionURLs': [],
                'channel': CHANNEL_NAME
            }
        }
        for conda_version in conda_search_result[conda_package]:
            newPackage.get("metadata").get("versions").append(conda_version.get('version'))
            newPackage.get("metadata").get("versionURLs").append(conda_version.get('url'))
        resource_metadata.append(newPackage)

    ALL_RESOURCES = resource_metadata


def get_resource(resource_name):
    # First see if resources are initialized
    if len(ALL_RESOURCES) == 0:
        fetch_resources()

    resource = [x for x in ALL_RESOURCES if x['name'] == resource_name]

    if len(resource) > 0:
        return resource[0]
    else:
        return None


def home(request):
    if len(ALL_RESOURCES) == 0:
        fetch_resources()

    # print(ALL_RESOURCES)

    # message_box = MessageBox(name='notification',
    #                          title='Application Install Status',
    #                          dismiss_button='Nevermind',
    #                          affirmative_button='Refresh',
    #                          affirmative_attributes='onClick=window.location.href=window.location.href;')

    tag_list = []

    # from distutils.sysconfig import get_python_lib
    # print(get_python_lib())

    # (conda_info_result, err, code) = run_command(Commands.INFO, ["--json"])
    # conda_info_result = json.loads(conda_info_result)
    # print(conda_info_result)
    # for resource in ALL_RESOURCES:
    #     resource['tag_class'] = ""
    #     if len(resource['metadata']['app_tags']) > 0:
    #         resource['tag_class'] = ' '.join(resource['metadata']['app_tags'])
    #         tag_list = tag_list + resource['metadata']['app_tags']

    # tag_list = list(set(tag_list))

    context = {'resources': ALL_RESOURCES,
               'resourcesJson': json.dumps(ALL_RESOURCES),
               # "install_message_box": message_box,
               "tags": tag_list}
    return render(request, 'warehouse/home.html', context)


def install(request):
    app_id = request.GET.get('name')
    app_version = request.GET.get('version')
    resource = get_resource(app_id)
    thread = threading.Thread(target=begin_install, args=(resource, app_version, get_channel_layer()))
    thread.start()
    return JsonResponse(resource)
