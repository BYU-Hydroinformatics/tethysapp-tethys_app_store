from django.shortcuts import render
from django.http import JsonResponse
from channels.layers import get_channel_layer
from conda.cli.python_api import Commands, run_command
from tethys_sdk.permissions import login_required

from packaging import version
import xml.etree.ElementTree as ET

import json
import threading
import sys

from .app import Warehouse as app
from .begin_install import begin_install
from .notifications import *

ALL_RESOURCES = []
CHANNEL_NAME = 'rfun'


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


@login_required()
def home(request):
    if len(ALL_RESOURCES) == 0:
        fetch_resources()

    tag_list = []

    # for resource in ALL_RESOURCES:
    #     resource['tag_class'] = ""
    #     if len(resource['metadata']['app_tags']) > 0:
    #         resource['tag_class'] = ' '.join(resource['metadata']['app_tags'])
    #         tag_list = tag_list + resource['metadata']['app_tags']

    # tag_list = list(set(tag_list))

    context = {'resources': ALL_RESOURCES,
               'resourcesJson': json.dumps(ALL_RESOURCES),
               "tags": tag_list}
    return render(request, 'warehouse/home.html', context)


def install(request):
    app_id = request.GET.get('name')
    app_version = request.GET.get('version')
    resource = get_resource(app_id)
    thread = threading.Thread(target=begin_install, args=(resource, app_version, get_channel_layer()))
    thread.start()
    return JsonResponse(resource)
