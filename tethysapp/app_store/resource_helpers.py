from django.core.cache import cache

import ast
import re
import semver
from tethys_portal import __version__ as tethys_version
import copy

import os
import json
import urllib
import shutil
from pkg_resources import parse_version
import yaml
import subprocess
from .utilities import get_available_stores_values
from .helpers import add_if_exists, check_if_app_installed,add_if_exists_keys, logger

CACHE_KEY = ""
# CACHE_KEY = "warehouse_app_resources"

# CHANNEL_NAME = 'tethysapp'


def clear_cache(data, channel_layer):
    cache.delete(CACHE_KEY)


def create_pre_multiple_stores_labels_obj(app_workspace, refresh=False, stores='all'):
    available_stores_data_dict = get_available_stores_values(stores)
    object_stores = {}
    ## fetch resources for each store and label
    for store in available_stores_data_dict:
        store_name = store['conda_channel']
        object_stores[store_name] = {}
        for conda_label in store['conda_labels']:
            cache_key = f'{store_name}_{conda_label}_app_resources'
            object_stores[store_name][conda_label] = get_resources_single_store(app_workspace, refresh, store_name,conda_label, cache_key=cache_key)
            # breakpoint()
    return object_stores

def get_new_stores_reformated_by_labels(object_stores):
    new_store_reformatted = {}
    for store in object_stores:
        new_store_reformatted[store] = {}
        list_labels_store = list(object_stores[store].keys())
        list_type_apps = list(object_stores[store][list_labels_store[0]].keys())
        for type_app  in list_type_apps:
            # breakpoint()
            if type_app != 'tethysVersion':
                new_store_reformatted[store][type_app] = merge_labels_single_store(object_stores[store],store,type_app)
    return new_store_reformatted

def get_stores_reformatted(app_workspace, refresh=False, stores='all'):
    # breakpoint()
    object_stores_raw = create_pre_multiple_stores_labels_obj(app_workspace, refresh,stores)
    object_stores_formatted_by_label = get_new_stores_reformated_by_labels(object_stores_raw)
    ## reformat for stores now
    object_stores_formatted_by_channel = get_stores_reformated_by_channel(object_stores_formatted_by_label)
    # breakpoint()
    list_stores_formatted_by_channel = reduce_level_obj(object_stores_formatted_by_channel)
    return list_stores_formatted_by_channel

def object_to_list (obj_con):
    new_list =[]
    for key in obj_con:
        new_list.append(obj_con[key])
    return new_list
def reduce_level_obj(complex_obj):
    for key in complex_obj:
        if type(complex_obj[key]) is dict:
            complex_obj[key] = object_to_list(complex_obj[key])
    return  complex_obj
def get_stores_reformated_by_channel(stores):
    app_channel_obj = get_app_channel_for_stores(stores)
    merged_channels_app = merge_channels_of_apps(app_channel_obj,stores)
    return merged_channels_app

def merge_channels_of_apps(app_channel_obj,stores):
    merged_channels_app = {}
    for channel in stores:
        for type_app in stores[channel]:
            if type_app not in merged_channels_app:
                merged_channels_app[type_app] = {}
            for app in stores[channel][type_app]:
                if app not in merged_channels_app[type_app]:
                    merged_channels_app[type_app][app] = {}
                if app not in app_channel_obj[type_app]:
                    continue
                for key in stores[channel][type_app][app]:
                    if key != 'name':
                        if key not in merged_channels_app[type_app][app]:
                            merged_channels_app[type_app][app][key] = {}
                        if channel in app_channel_obj[type_app][app]:
                            merged_channels_app[type_app][app][key][channel] = stores[channel][type_app][app][key][channel]
                    else:
                        merged_channels_app[type_app][app][key] = stores[channel][type_app][app][key]

    return merged_channels_app


def get_app_channel_for_stores(stores):
    app_channel_obj = {}
    for channel in stores:
        for type_apps in stores[channel]:
            if type_apps not in app_channel_obj:
                app_channel_obj[type_apps] ={}
            for app in stores[channel][type_apps]:
                if app not in app_channel_obj[type_apps]:
                    app_channel_obj[type_apps][app] = []
                    app_channel_obj[type_apps][app].append(channel)
                else:
                    if channel not in app_channel_obj[type_apps][app]:
                        app_channel_obj[type_apps][app].append(channel)
    return app_channel_obj

def get_app_level_for_store(store,type_apps):
    # breakpoint()
    apps_levels = {}
    levels = list(store.keys())
    for level in levels:
        apps = list(store[level][type_apps].keys())
        for app in apps:
            if app in apps_levels:
                apps_levels[app].append(level)
            else:
                apps_levels[app] = []
                apps_levels[app].append(level)
    return apps_levels

def merge_levels_for_app_in_store(apps_channels,store,channel,type_apps):
    new_store_label_obj = {}
    for app in apps_channels:
        if app not in new_store_label_obj:
            new_store_label_obj[app] = {}
        for label in store:

            if label not in apps_channels[app]:
                # breakpoint()
                continue
            for key in store[label][type_apps][app]:
                if key != 'name':
                    if key not in  new_store_label_obj[app]:
                        new_store_label_obj[app][key] = {
                            channel:{}
                        }
                    # try:
                    for label_app in store[label][type_apps][app][key][channel]:
                        new_store_label_obj[app][key][channel][label_app] = store[label][type_apps][app][key][channel][label_app]
                    # except TypeError:
                    #     breakpoint()
                    #     x  = "hi error"
    return new_store_label_obj


def get_app_label_obj_for_store(store,type_apps):
    apps_label = {}
    labels = list(store.keys())
    for label in labels:
        apps = list(store[label][type_apps].keys())
        for app in apps:
            if app in apps_label:
                apps_label[app].append(label)
            else:
                apps_label[app] = []
                apps_label[app].append(label)
    return apps_label

def merge_labels_for_app_in_store(apps_label,store,channel,type_apps):
    new_store_label_obj = {}
    for app in apps_label:
        if app not in new_store_label_obj:
            new_store_label_obj[app] = {}
        for label in store:
            # if len(apps_label[app]) > 1:
            #     breakpoint()
            if label not in apps_label[app]:
                # breakpoint()
                continue
            for key in store[label][type_apps][app]:
                if key != 'name':
                    if key not in  new_store_label_obj[app]:
                        new_store_label_obj[app][key] = {
                            channel:{}
                        }
                    # try:
                    for label_app in store[label][type_apps][app][key][channel]:
                        new_store_label_obj[app][key][channel][label_app] = store[label][type_apps][app][key][channel][label_app]
                else:
                    new_store_label_obj[app][key] = store[label][type_apps][app][key]
                    # except TypeError:
                    #     breakpoint()
                    #     x  = "hi error"
    return new_store_label_obj

def merge_labels_single_store(store,channel,type_apps):
    # breakpoint()
    apps_labels = get_app_label_obj_for_store(store,type_apps)
    merged_label_store = merge_labels_for_app_in_store(apps_labels,store,channel,type_apps)
    return merged_label_store


def get_resources_single_store(app_workspace, require_refresh, conda_package,conda_label,cache_key):
    installed_apps = {}
    available_apps = {}
    incompatible_apps = {}
    all_resources = fetch_resources_new(app_workspace, require_refresh, conda_package, conda_label,cache_key)
    tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
    for resource in all_resources:
        if resource["installed"][conda_package][conda_label]:
            installed_apps[resource['name']] = resource
        # else:
        # tethys_version_regex = '4.0.0'
        tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
        # breakpoint()
        add_compatible = False
        add_incompatible = False
        new_compatible_app = copy.deepcopy(resource)
        new_compatible_app['versions'][conda_package][conda_label] = []
        new_incompatible_app = copy.deepcopy(new_compatible_app)
        for version in resource['versions'][conda_package][conda_label]:
            # debugging
            # if resource['name'] == 'test1app' and conda_label == 'dev':
            #     breakpoint()
            #     x = 'hola'

            # Assume if not found, that it is compatible with Tethys Platform 3.4.4
            compatible_tethys_version = "<=3.4.4"
            if version in resource['compatibility'][conda_package][conda_label]:
                compatible_tethys_version = resource['compatibility'][conda_package][conda_label][version]
            if semver.match(tethys_version_regex, compatible_tethys_version):
                add_compatible = True
                new_compatible_app['versions'][conda_package][conda_label].append(version)
            else:
                add_incompatible = True
                new_incompatible_app['versions'][conda_package][conda_label].append(version)

        if add_compatible:
            available_apps[resource['name']] = new_compatible_app
        if add_incompatible:
            # breakpoint()
            incompatible_apps[resource['name']] = new_incompatible_app

    # Get any apps installed via GitHub install process
    # github_apps = get_github_install_metadata(app_workspace)
    github_apps = []


    return_object = {
        'availableApps': available_apps,
        # 'installedApps': installed_apps + github_apps,
        'installedApps': installed_apps,
        'incompatibleApps': incompatible_apps,
        'tethysVersion': tethys_version_regex,
    }

    return return_object



def fetch_resources_new(app_workspace, refresh=False, conda_package="tethysapp", conda_label="main" , cache_key=None):
    
    # breakpoint()
    CHANNEL_NAME = conda_package

    if conda_label != 'main':
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
        if 'error' in conda_search_result and 'The following packages are not available from current channels' in conda_search_result['error']:
            logger.info(f'no packages found with the label {conda_label} in channel {CHANNEL_NAME}')    
            return resource_metadata
        for app_package in conda_search_result:

            installed_version = check_if_app_installed(app_package)

            newPackage = {
                'name': app_package,
                'installed': 
                {
                    conda_package: {
                        conda_label: False
                    }
                },
                'versions': 
                {
                    conda_package: {
                        conda_label: []
                    }
                },
                'versionURLs': 
                {
                    conda_package: {
                        conda_label: []
                    }
                },
                'channels_and_labels': 
                {
                    conda_package: {
                        conda_label: []
                    }
                },
                'timestamp':{
                    conda_package:{
                        conda_label: conda_search_result[app_package][-1]["timestamp"]
                    }
                },
                'compatibility': {
                    conda_package:{
                        conda_label: {}
                    }
                },
                'license':{
                    conda_package:{
                        conda_label: None
                    }
                },
                'licenses':{
                    conda_package:{
                        conda_label: []
                    }
                }
                
            }
            # breakpoint()
            if "license" in conda_search_result[app_package][-1]:
                newPackage["license"][conda_package][conda_label] = conda_search_result[app_package][-1]["license"]

            if installed_version['isInstalled']:
                if CHANNEL_NAME == installed_version['channel']:
                    newPackage["installed"][conda_package][conda_label] = True
                    newPackage["installedVersion"] = {
                        conda_package:{}
                    }
                    newPackage["installedVersion"][conda_package][conda_label] = installed_version['version']
            for conda_version in conda_search_result[app_package]:
                newPackage.get("versions").get(f"{conda_package}").get(f"{conda_label}").append(conda_version.get('version'))
                newPackage.get("versionURLs").get(f"{conda_package}").get(f"{conda_label}").append(conda_version.get('url'))
                newPackage.get("licenses").get(f"{conda_package}").get(f"{conda_label}").append(conda_version.get('license'))

                # breakpoint()

                if "license" in conda_version:
                    try:
                        license_json = json.loads(conda_version['license'].replace("', '", '", "').replace("': '", '": "').replace("'}", '"}').replace("{'", '{"'))
                        if 'tethys_version' in license_json:
                            # breakpoint()
                            newPackage["compatibility"][conda_package][conda_label][conda_version.get('version')] = license_json.get('tethys_version')
                            # newPackage.get("compatibility").get(f"{conda_package}").get(f"{conda_label}").append(conda_version.get('license'))
                    except (ValueError, TypeError):
                        pass

            resource_metadata.append(newPackage)

        
        resource_metadata = process_resources_new(resource_metadata, app_workspace, conda_package, conda_label)
        # breakpoint()
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
    # breakpoint()
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

        # breakpoint()
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
            # app["updateAvailable"][conda_channel][conda_label] = True
            # breakpoint()
            # if app['name'] == 'test1app':
                # breakpoint()
                # print("hola")

            if 'installedVersion' in app:
                # breakpoint()
                if(app["latestVersion"][conda_channel][conda_label].find("*") == False):
                    if parse_version(app["latestVersion"][conda_channel][conda_label]) > parse_version(app["installedVersion"][conda_channel][conda_label]):
                        app["updateAvailable"] = {
                            conda_channel: {
                                conda_label: True
                            }
                        }
                else:
                    app["updateAvailable"] = {
                        conda_channel: {
                            conda_label: False
                        }
                    }
            else:
                app["updateAvailable"] = {
                    conda_channel: {
                        conda_label: False
                    }
                }
        latest_version_url = app.get("versionURLs").get(f"{conda_channel}").get(f"{conda_label}")[-1]
        file_name = latest_version_url.split('/')
        folder_name = app.get("name")

        # Check for metadata in the Search Description
        # That path will work for newly submitted apps with warehouse ver>0.25

        try:
            if "license" not in app or app['license'][conda_channel][conda_label] is None:
                raise ValueError
            license_metadata = json.loads(app["license"][conda_channel][conda_label]
                .replace("', '", '", "').replace("': '", '": "').replace("'}", '"}').replace("{'", '{"'))
            
            ### create new one
            app = add_if_exists_keys(license_metadata, app, [
                'author', 'description', 'license', 'author_email', 'keywords'],conda_channel,conda_label)
            
            if "url" in license_metadata:
                app['dev_url'] = {
                    conda_channel:{
                        conda_label:''
                    }
                }
                app['dev_url'][conda_channel][conda_label] = license_metadata["url"]
            
            else:
                app['dev_url'] = {
                    conda_channel:{
                        conda_label:''
                    }
                }
                app['dev_url'][conda_channel][conda_label] = ''
            # if "tethys_version" in license_metadata:
            #     # breakpoint()
            #     app.get("compatibility").get(f"{conda_channel}").get(f"{conda_label}")[license_metadata['version']] = license_metadata['tethys_version']  # noqa: E501

        except (ValueError, TypeError):
            # There wasn't json found in license. Get Metadata from downloading the file
            download_path = os.path.join(workspace_folder, conda_channel,conda_label, file_name[-1])
            # extract_path = os.path.join(workspace_folder, file_name[-1])
            output_path = os.path.join(workspace_folder,conda_channel,conda_label,folder_name)
            if not os.path.exists(download_path):
                if not os.path.exists(os.path.join(workspace_folder, conda_channel,conda_label)):
                    os.makedirs(os.path.join(workspace_folder, conda_channel,conda_label))

                logger.info("License field metadata not found. Downloading: " + file_name[-1])
                urllib.request.urlretrieve(latest_version_url, download_path)

                if os.path.exists(output_path):
                    # Clear the output extracted folder
                    shutil.rmtree(output_path)

                shutil.unpack_archive(download_path, output_path)

            # app["filepath"] = output_path
            app["filepath"] = {
                conda_channel: {
                    conda_label: output_path
                }
            }

            # Get Meta.Yaml for this file
            try:
                meta_yaml_path = os.path.join(output_path, 'info', 'recipe', 'meta.yaml')
                if os.path.exists(meta_yaml_path):
                    with open(meta_yaml_path) as f:
                        meta_yaml = yaml.safe_load(f)
                        # Add metadata to the resources object.
                        
                        attr_about =['author', 'description', 'dev_url', 'license']
                        attr_extra =['author_email', 'keywords']

                        app = add_if_exists_keys(meta_yaml.get('about'), app, attr_about, conda_channel,conda_label)
                        app = add_if_exists_keys(meta_yaml.get('extra'), app, attr_extra,conda_channel,conda_label)
                        if 'dev_url' not in app:
                            app['dev_url'] = {
                                conda_channel:{
                                    conda_label:''
                                }
                            }
                            app['dev_url'][conda_channel][conda_label] = ''
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

def get_resource_new(resource_name,channel,label, app_workspace):
    all_resources = fetch_resources_new(app_workspace= app_workspace,conda_package=channel, conda_label=label)
    # all_resources = fetch_resources(app_workspace)

    resource = [x for x in all_resources if x['name'] == resource_name]

    if len(resource) > 0:
        return resource[0]
    else:
        return None
