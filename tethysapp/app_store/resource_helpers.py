from django.core.cache import cache

import ast
import re
import semver
from tethys_portal import __version__ as tethys_version

import os
import json
import urllib
import shutil
import yaml
import subprocess
from .utilities import get_available_stores_values
from .helpers import add_if_exists, check_if_app_installed, logger

CACHE_KEY = ""
# CACHE_KEY = "warehouse_app_resources"

# CHANNEL_NAME = 'tethysapp'


def clear_cache(data, channel_layer):
    cache.delete(CACHE_KEY)


def fetch_resources_multiple_labels(app_workspace, refresh=False, conda_package="tethysapp", cache_key=None):
    available_stores_data_dict = get_available_stores_values()
    object_stores = {}
    ## fetch resources for each store and label
    for store in available_stores_data_dict:
        object_stores[store] = {}
        for conda_label in store['conda_labels']:
           object_stores[store][conda_label] = get_resources_single_store(app_workspace, refresh, conda_package,conda_label, cache_key=None)
    return object_stores


def get_resources_single_store(app_workspace, require_refresh,conda_label, conda_package,cache_key):
    installed_apps = []
    available_apps = []
    incompatible_apps = []
    all_resources = fetch_resources_new(app_workspace, require_refresh, conda_package, conda_label,cache_key)
    for resource in all_resources:
        if resource["installed"]:
            installed_apps.append(resource)
        else:
            # tethys_version_regex = '4.0.0'
            tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
            # breakpoint()
            add_compatible = False
            add_incompatible = False
            new_compatible_app = copy.deepcopy(resource)
            new_compatible_app['metadata']['versions'] = []
            new_incompatible_app = copy.deepcopy(new_compatible_app)
            for version in resource['metadata']['versions']:
                # Assume if not found, that it is compatible with Tethys Platform 3.4.4
                compatible_tethys_version = "<=3.4.4"
                if version in resource['metadata']['compatibility'].keys():
                    compatible_tethys_version = resource['metadata']['compatibility'][version]
                if semver.match(tethys_version_regex, compatible_tethys_version):
                    add_compatible = True
                    new_compatible_app['metadata']['versions'].append(version)
                else:
                    add_incompatible = True
                    new_incompatible_app['metadata']['versions'].append(version)

            if add_compatible:
                available_apps.append(new_compatible_app)
            if add_incompatible:
                incompatible_apps.append(new_incompatible_app)

    # Get any apps installed via GitHub install process
    # github_apps = get_github_install_metadata(app_workspace)
    github_apps = []


    return_object = {
        'availableApps': available_apps,
        'installedApps': installed_apps + github_apps,
        'incompatibleApps': incompatible_apps,
        'tethysVersion': tethys_version_regex,
    }

    return return_object






def fetch_resources_new(app_workspace, refresh=False, conda_package="tethysapp", conda_label="main" , cache_key=None):
    CHANNEL_NAME = conda_package

    if conda_label is not 'main':
        CHANNEL_NAME = f'{conda_package}/label/{conda_label}'
    
    CACHE_KEY = cache_key

    cache.get(CACHE_KEY)
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
                'installed': 
                {
                    CHANNEL_NAME: {
                        conda_label: False
                    }
                },
                'versions': 
                {
                    CHANNEL_NAME: []
                },
                'versionURLs': 
                {
                    CHANNEL_NAME: []
                },
                'channels_and_labels': 
                {
                    CHANNEL_NAME:[]
                },
                'timestamp':{
                    CHANNEL_NAME:{
                        conda_label: conda_search_result[conda_package][-1]["timestamp"]
                    }
                },
                'compatibility': {
                    CHANNEL_NAME:{
                        conda_label: ''
                    }
                }
                
            }

            if "license" in conda_search_result[conda_package][-1]:
                newPackage["license"] = {
                    CHANNEL_NAME: {}
                }
                newPackage["license"][CHANNEL_NAME][conda_label] = conda_search_result[conda_package][-1]["license"]

            if installed_version:
                newPackage["installed"][CHANNEL_NAME][conda_label] = True
                newPackage["installedVersion"] = {
                    CHANNEL_NAME:{}
                }
                newPackage["installedVersion"][CHANNEL_NAME][conda_label] = installed_version
            for conda_version in conda_search_result[conda_package]:
                newPackage.get("versions").get(f"{CHANNEL_NAME}").get(f"{conda_label}").append(conda_version.get('version'))
                newPackage.get("versionURLs").get(f"{CHANNEL_NAME}").get(f"{conda_label}").append(conda_version.get('url'))

            resource_metadata.append(newPackage)

        resource_metadata = process_resources(resource_metadata, app_workspace)
        cache.set(CACHE_KEY, resource_metadata)
        return resource_metadata
    else:
        logger.info("Found in cache")
        return cache.get(CACHE_KEY)



def fetch_resources(app_workspace, refresh=False, conda_package="tethysapp", cache_key=None):
    CHANNEL_NAME = conda_package
    CACHE_KEY = cache_key
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

    cache.get(CACHE_KEY)
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
                    'timestamp': conda_search_result[conda_package][-1]["timestamp"],
                    'compatibility': {}
                }
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


def process_resources_new(resources, app_workspace,conda_channel, conda_label):

    for app in resources:
        workspace_folder = os.path.join(app_workspace.path, 'apps')
        if not os.path.exists(workspace_folder):
            os.makedirs(workspace_folder)

        tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
        # Set Latest Version
        app["latestVersion"] = {
            conda_channel: {}
        }
        app["latestVersion"][conda_channel][conda_label] = app.get("versions").get(f"{conda_channel}").get(f"{conda_label}")[-1]

        # Check if latest version is compatible. If not, append an asterisk
        license = app.get("license").get(f"{conda_channel}").get(f"{conda_label}")
        comp_dict = None
        compatible = None
        try:
            comp_dict = ast.literal_eval(license)
        except Exception:
            pass
        if comp_dict and 'tethys_version' in comp_dict:
            compatible = comp_dict['tethys_version']

        if compatible is None:
            compatible = "<=3.4.4"

        if not semver.match(tethys_version_regex, compatible):
            app["latestVersion"][conda_channel][conda_label] = app["latestVersion"][conda_channel][conda_label] + "*"

        # if(app['installed']):
        #     app["updateAvailable"] = version.parse(app['installedVersion']) < version.parse(app['latestVersion'])
        # FOR Debugging only. @TODO: Remove
        if(app['installed']):
            app["updateAvailable"] = True

        latest_version_url = app.get("versionURLs").get(f"{conda_channel}").get(f"{conda_label}")[-1]
        file_name = latest_version_url.split('/')
        folder_name = app.get("name")

        # Check for metadata in the Search Description
        # That path will work for newly submitted apps with warehouse ver>0.25

        try:
            if "license" not in app:
                raise ValueError
            license_metadata = json.loads(app["license"][conda_channel][conda_label]
                .replace("', '", '", "').replace("': '", '": "').replace("'}", '"}').replace("{'", '{"'))
            ### create new one
            app['metadata'] = add_if_exists(license_metadata, app, [
                'author', 'description', 'license', 'author_email', 'keywords'])
            
            if "url" in license_metadata:
                app['dev_url'][conda_channel][conda_label] = license_metadata["url"]
            if "tethys_version" in license_metadata:
                app.get("metadata").get("compatibility")[license_metadata['version']] = license_metadata['tethys_version']  # noqa: E501

        except (ValueError, TypeError):
            # There wasn't json found in license. Get Metadata from downloading the file
            download_path = os.path.join(workspace_folder, file_name[-1])
            # extract_path = os.path.join(workspace_folder, file_name[-1])
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



def process_resources(resources, app_workspace):

    for app in resources:
        workspace_folder = os.path.join(app_workspace.path, 'apps')
        if not os.path.exists(workspace_folder):
            os.makedirs(workspace_folder)

        tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
        # Set Latest Version
        app["latestVersion"] = app.get("metadata").get("versions")[-1]

        # Check if latest version is compatible. If not, append an asterisk
        license = app.get("metadata").get("license")
        comp_dict = None
        compatible = None
        try:
            comp_dict = ast.literal_eval(license)
        except Exception:
            pass
        if comp_dict and 'tethys_version' in comp_dict:
            compatible = comp_dict['tethys_version']

        if compatible is None:
            compatible = "<=3.4.4"

        if not semver.match(tethys_version_regex, compatible):
            app["latestVersion"] = app["latestVersion"] + "*"

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
                app.get("metadata").get("compatibility")[license_metadata['version']] = license_metadata['tethys_version']  # noqa: E501

        except (ValueError, TypeError):
            # There wasn't json found in license. Get Metadata from downloading the file
            download_path = os.path.join(workspace_folder, file_name[-1])
            # extract_path = os.path.join(workspace_folder, file_name[-1])
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
