from django.core.cache import cache
from packaging import version

import os
import json
import urllib
import shutil
import yaml
import subprocess

from .helpers import *

CACHE_KEY = "warehouse_app_resources"
CHANNEL_NAME = 'tethysapp'


def clear_cache(data, channel_layer):
    cache.delete(CACHE_KEY)


def fetch_resources(app_workspace, refresh=False):

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

    all_resources = cache.get(CACHE_KEY)
    if (cache.get(CACHE_KEY) is None) or refresh:

        # Look for packages:
        logger.info("Refreshing list of apps cache")

        conda_search_result = subprocess.run(['conda', 'search', "-c", CHANNEL_NAME, "--override-channels",
                                              "-i", "--json"], stdout=subprocess.PIPE)

        conda_search_result = json.loads(conda_search_result.stdout)
        resource_metadata = []
        logger.info("Total Apps Found:" + str(len(conda_search_result)))
        for conda_package in conda_search_result:
            installed_version = check_if_app_installed(conda_package)
            newPackage = {
                'name': conda_package,
                'installed': False,
                'metadata': {
                    'versions': [],
                    'versionURLs': [],
                    'channel': CHANNEL_NAME,
                    'timestamp': conda_search_result[conda_package][-1]["timestamp"]
                },
                'tethys_version': '<4.0.0'  # assume smaller than version 4 to begin with (see license_metadata tethys_version conditional)  # noqa: E501
            }

            if "license" in conda_search_result[conda_package][-1]:
                newPackage["metadata"]["license"] = conda_search_result[conda_package][-1]["license"]

            if installed_version:
                newPackage["installed"] = True
                newPackage["installedVersion"] = installed_version
            for conda_version in conda_search_result[conda_package]:
                newPackage.get("metadata").get("versions").append(conda_version.get('version'))
                newPackage.get("metadata").get("versionURLs").append(conda_version.get('url'))
            resource_metadata.append(newPackage)

        resource_metadata = process_resources(resource_metadata, app_workspace)
        cache.set(CACHE_KEY, resource_metadata)
        return resource_metadata
    else:
        logger.info("Found in cache")
        return cache.get(CACHE_KEY)


def process_resources(resources, app_workspace):

    for app in resources:
        workspace_folder = os.path.join(app_workspace.path, 'apps')
        if not os.path.exists(workspace_folder):
            os.makedirs(workspace_folder)

        # Set Latest Version
        app["latestVersion"] = app.get("metadata").get("versions")[-1]

        # if(app['installed']):
        #     app["updateAvailable"] = version.parse(app['installedVersion']) < version.parse(app['latestVersion'])
        # FOR Debugging only. @TODO: Remove
        if(app['installed']):
            app["updateAvailable"] = True

        latest_version_url = app.get("metadata").get("versionURLs")[-1]
        file_name = latest_version_url.split('/')
        folder_name = app.get("name")

        # Check for metadata in the Search Description
        # That path will work for newly submitted apps with warehouse ver>0.25

        try:
            if "license" not in app.get("metadata"):
                raise ValueError

            license_metadata = json.loads(app.get("metadata").get(
                "license").replace("', '", '", "').replace("': '", '": "').replace("'}", '"}').replace("{'", '{"'))
            app['metadata'] = add_if_exists(license_metadata, app['metadata'], [
                'author', 'description', 'license', 'author_email', 'keywords'])
            if "url" in license_metadata:
                app['metadata']['dev_url'] = license_metadata["url"]
            if "tethys_version" in license_metadata:
                app['tethys_version'] = license_metadata["tethys_version"]

        except (ValueError, TypeError) as e:
            # There wasn't json found in license. Get Metadata from downloading the file
            download_path = os.path.join(workspace_folder, file_name[-1])
            extract_path = os.path.join(workspace_folder, file_name[-1])
            output_path = os.path.join(workspace_folder, folder_name)
            if not os.path.exists(download_path):
                logger.info("License field metadata not found. Downloading: " + file_name[-1])
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
                logger.info("Error happened while downloading package for metadata")
                logger.error(e)

    return resources


def get_resource(resource_name, app_workspace):

    all_resources = fetch_resources(app_workspace)
    resource = [x for x in all_resources if x['name'] == resource_name]

    if len(resource) > 0:
        return resource[0]
    else:
        return None
