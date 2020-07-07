from django.shortcuts import render
from django.http import JsonResponse
from channels.layers import get_channel_layer
from conda.cli.python_api import Commands, run_command
from tethys_sdk.permissions import login_required
from tethys_sdk.workspaces import app_workspace

from packaging import version
import xml.etree.ElementTree as ET

import json
import threading
import sys
import os
import urllib.request
import shutil
import yaml

from .app import Warehouse as app
from .begin_install import begin_install
from .notifications import *
from .helpers import add_if_exists

ALL_RESOURCES = []
CHANNEL_NAME = 'rfun'


def fetch_resources(app_workspace):
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
    # print(conda_search_result)
    conda_search_result = json.loads(conda_search_result)

    resource_metadata = []
    for conda_package in conda_search_result:
        # print(conda_package)
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

    resource_metadata = process_resources(resource_metadata, app_workspace)
    ALL_RESOURCES = resource_metadata


def process_resources(resources, app_workspace):

    for app in resources:
        workspace_folder = os.path.join(app_workspace.path, 'apps')
        if not os.path.exists(workspace_folder):
            os.makedirs(workspace_folder)
        latest_version_url = app.get("metadata").get("versionURLs")[-1]
        file_name = latest_version_url.split('/')
        folder_name = app.get("name")
        download_path = os.path.join(workspace_folder, file_name[-1])
        extract_path = os.path.join(workspace_folder, file_name[-1])
        output_path = os.path.join(workspace_folder, folder_name)
        if not os.path.exists(download_path):
            print("Downloading: " + file_name[-1])
            urllib.request.urlretrieve(latest_version_url, download_path)

            if os.path.exists(output_path):
                # Clear the output extracted folder
                shutil.rmtree(output_path)

            shutil.unpack_archive(download_path, output_path)

        app["filepath"] = output_path

        # Get Meta.Yaml for this file
        try:
            meta_yaml_path = os.path.join(output_path, 'info', 'recipe', 'meta.yaml')
            if os.path.exists(meta_yaml_path):
                with open(meta_yaml_path) as f:
                    meta_yaml = yaml.safe_load(f)
                    # Add metadata to the resources object.
                    app['metadata'] = add_if_exists(meta_yaml.get('about'), app['metadata'], [
                                                    'author', 'description', 'dev_url', 'license'])
                    app['metadata'] = add_if_exists(meta_yaml.get('extra'), app['metadata'], [
                        'author_email', 'keywords'])

        except Exception as e:
            print("sadsdf")
            print(e)

    return resources


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
@app_workspace
def home(request, app_workspace):

    if len(ALL_RESOURCES) == 0:
        fetch_resources(app_workspace)

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
