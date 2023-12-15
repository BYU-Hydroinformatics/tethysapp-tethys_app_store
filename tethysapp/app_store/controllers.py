import re
import semver
import os
import json
from tethys_portal import __version__ as tethys_version
from django.http import JsonResponse
from django.shortcuts import render
from tethys_sdk.routing import controller

import copy

from .resource_helpers import fetch_resources, get_stores_reformatted
from .helpers import get_github_install_metadata

from .app import AppStore as app
from .utilities import decrypt
ALL_RESOURCES = []
CACHE_KEY = "warehouse_app_resources"


@controller(
    name='home',
    url='app-store',
    permissions_required='use_app_store',
    app_workspace=True,
)
def home(request,app_workspace):
    available_stores_data_dict = app.get_custom_setting("stores_settings")['stores']
    encryption_key = app.get_custom_setting("encryption_key")
    for store in available_stores_data_dict:
        store['github_token'] = decrypt(store['github_token'],encryption_key)
    # available_stores_json_path = os.path.join(app_workspace.path, 'stores.json')
    # available_stores_data_dict = {}
    # with open(available_stores_json_path) as available_stores_json_file:
    #     available_stores_data_dict = json.load(available_stores_json_file)['stores']
    
    print(available_stores_data_dict)
    
    context = {
        'storesData':available_stores_data_dict,
        'show_stores': True if len(available_stores_data_dict) > 0 else False
    }

    return render(request, 'app_store/home.html', context)

@controller(
    name='get_available_stores',
    url='app-store/get_available_stores',
    permissions_required='use_app_store',
    app_workspace=True,
)
def get_available_stores(request,app_workspace):
    # breakpoint()
    available_stores_data_dict = app.get_custom_setting("stores_settings")
    encryption_key = app.get_custom_setting("encryption_key")
    for store in available_stores_data_dict['stores']:
        store['github_token'] = decrypt(store['github_token'],encryption_key)

    # available_stores_json_path = os.path.join(app_workspace.path, 'stores.json')
    # available_stores_data_dict = {}
    # with open(available_stores_json_path) as available_stores_json_file:
    #     available_stores_data_dict = json.load(available_stores_json_file)

    return JsonResponse(available_stores_data_dict)

# went through the pull request comments, refactored code, corrected bugs, and create new tests
# solved a bug with the versioning in the submissions, and working on the installation of apps with multiple stores.

# create list of all apps in stores without repetitive values
def find_apps_in_stores(stores, app_list):
    for store in stores:
        for app in store:
            if app['name'] not in app_list:
                app_list.append(app['name'])
    return app_list

def generate_empty_multi_store_apps_object(app_list):
    return_obj = {}
    for app in app_list:
        return_obj[app] = {
            'name': {},
            'installed': {},
            'metadata': {},
            'latestVersion':{}
        }

    return return_obj

def populate_multi_store_apps_object(stores, multi_store_apps_object):
    # breakpoint()
    for store in stores:
        for app in store:
            for key in app:
                if key in multi_store_apps_object[app['name']]: 
                    multi_store_apps_object[app['name']][key][app['metadata']['channel']] = app[key]

    return multi_store_apps_object

def object_to_list(request_obj):
    return_list = []
    for key in request_obj:
        return_list.append(request_obj[key])
    return return_list

def get_multi_store_obj_list(stores):
    app_list = []
    # breakpoint()
    app_list = find_apps_in_stores(stores, app_list)
    multi_store_apps_object = generate_empty_multi_store_apps_object(app_list)
    multi_store_apps_object = populate_multi_store_apps_object(stores, multi_store_apps_object)
    multi_store_apps_object = make_single_name(multi_store_apps_object)
    multi_store_apps_list = object_to_list(multi_store_apps_object)
    return multi_store_apps_list

def make_single_name(multi_store_apps_object):
    for key in multi_store_apps_object:
        # breakpoint()
        for store_name in multi_store_apps_object[key]['name']:
            multi_store_apps_object[key]['name'] = multi_store_apps_object[key]['name'][store_name]
            break
    return multi_store_apps_object

def preprocess_single_store(conda_packages,require_refresh,app_workspace):
    pre_processing_dict = {
        'availableApps': [],
        'installedApps': [],
        'incompatibleApps': [],
        'tethysVersion': []
    }

    for conda_package in conda_packages:
        cache_key = f'{conda_package}_app_resources'
        resources_single_store = get_resources_single_store(app_workspace, require_refresh, conda_package,cache_key)
        # breakpoint()
        pre_processing_dict['availableApps'].append(resources_single_store['availableApps'])
        pre_processing_dict['installedApps'].append(resources_single_store['installedApps'])
        pre_processing_dict['incompatibleApps'].append(resources_single_store['incompatibleApps'])
        pre_processing_dict['tethysVersion'].append({f'{conda_package}':resources_single_store['tethysVersion']})
    
    return pre_processing_dict

@controller(
    name='get_merged_resources',
    url='app-store/get_merged_resources',
    permissions_required='use_app_store',
    app_workspace=True,
)
def get_resources_multiple_stores(request, app_workspace):
    # conda_packages = request.GET.getlist('conda_channels[]')
    stores_active = request.GET.get('active_store')
    require_refresh = request.GET.get('refresh', '') == "true"
    object_stores_formatted_by_label_and_channel = get_stores_reformatted(app_workspace, refresh=False, stores=stores_active)
    # breakpoint()
    tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)
    object_stores_formatted_by_label_and_channel['tethysVersion'] = tethys_version_regex
    
    # pre_processing_dict = preprocess_single_store(conda_packages,require_refresh,app_workspace)

    # return_object = {
    #     'availableApps': [],
    #     'installedApps': [],
    #     'incompatibleApps': [],
    #     'tethysVersion': [],
    # }
    # # breakpoint()
    # return_object['availableApps'] = get_multi_store_obj_list(pre_processing_dict['availableApps'])
    # return_object['installedApps'] = get_multi_store_obj_list(pre_processing_dict['installedApps'])
    # return_object['incompatibleApps'] = get_multi_store_obj_list(pre_processing_dict['incompatibleApps'])
    # return_object['tethysVersion'] = pre_processing_dict['tethysVersion']

    return JsonResponse(object_stores_formatted_by_label_and_channel)


 
def get_resources_single_store(app_workspace, require_refresh, conda_package,cache_key):
    installed_apps = []
    available_apps = []
    incompatible_apps = []
    all_resources = fetch_resources(app_workspace, require_refresh, conda_package,cache_key)
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

@controller(
    name='get_resources',
    url='app-store/get_resources',
    permissions_required='use_app_store',
    app_workspace=True,
)
def get_resources(request, app_workspace):
    # breakpoint()
    conda_package = request.GET.get('conda_channel')
    require_refresh = request.GET.get('refresh', '') == "true"
    # Always require refresh
    cache_key = f'{conda_package}_app_resources'
    all_resources = fetch_resources(app_workspace, require_refresh, conda_package,cache_key)
    # all_resources = fetch_resources(app_workspace, require_refresh)

    installed_apps = []
    available_apps = []
    incompatible_apps = []

    # breakpoint()
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
    github_apps = get_github_install_metadata(app_workspace)
    # breakpoint()
    context = {
        'availableApps': available_apps,
        'installedApps': installed_apps + github_apps,
        'incompatibleApps': incompatible_apps,
        'tethysVersion': tethys_version_regex,
    }

    return JsonResponse(context)
