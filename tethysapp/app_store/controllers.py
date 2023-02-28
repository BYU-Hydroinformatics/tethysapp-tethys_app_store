import re
import semver
import os
import json
from tethys_portal import __version__ as tethys_version
from django.http import JsonResponse
from django.shortcuts import render
from tethys_sdk.routing import controller

import copy

from .resource_helpers import fetch_resources
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
        'show_stores': True if len(available_stores_data_dict) > 1 else False
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

def return_merge_stores(store,resources_list, merged_list,type_list_resource):
    for available_app in resources_list[type_list_resource]:
        store_available_object = {}
        for key in available_app:
            if key is not 'name':
                if not any(x.name == available_app['name'] for x in merged_list[type_list_resource]):
                    store_available_object[key]= []
                    obj_re = {f'{store}': available_app[key]}
                    store_available_object[key].append(obj_re)
                    merged_list[type_list_resource].append(store_available_object)
                else:
                    index_app = next((i for i, d in enumerate(merged_list[type_list_resource]) if d['name'] == available_app['name']), None)
                    obj_re = {f'{store}': available_app[key]}
                    merged_list[type_list_resource][index_app].append(obj_re)
            else:
                store_available_object[key] = available_app[key]
                merged_list[type_list_resource].append(store_available_object)


def get_resources_multiple_stores(request, app_workspace):
    conda_packages = request.GET.get('conda_channels')
    require_refresh = request.GET.get('refresh', '') == "true"
    pre_processing_dict = {
        'availableApps': [],
        'installedApps': [],
        'incompatibleApps': [],
        'tethysVersion': []
    }

    for conda_package in conda_packages:
        cache_key = f'{conda_package}_app_resources'
        resources_single_store = get_resources_single_store(app_workspace, require_refresh, conda_package,cache_key)
        return_merge_stores(conda_package,resources_single_store,pre_processing_dict,'availableApps')
        return_merge_stores(conda_package,resources_single_store,pre_processing_dict,'installedApps')
        return_merge_stores(conda_package,resources_single_store,pre_processing_dict,'incompatibleApps')
        return_merge_stores(conda_package,resources_single_store,pre_processing_dict,'tethysVersion')

        # for available_app in resources_single_store['availableApps']:
        #     store_available_object = {}
        #     for key in available_app:
        #         if key is not 'name':
        #             if not any(x.name == available_app['name'] for x in pre_processing_dict['availableApps']):
        #                 store_available_object[key]= []
        #                 obj_re = {f'{conda_package}': available_app[key]}
        #                 store_available_object[key].append(obj_re)
        #                 pre_processing_dict['availableApps'].append(store_available_object)
        #             else:
        #                 index_app = next((i for i, d in enumerate(pre_processing_dict['availableApps']) if d['name'] == available_app['name']), None)
        #                 obj_re = {f'{conda_package}': available_app[key]}
        #                 pre_processing_dict['availableApps'][index_app].append(obj_re)
        #         else:
        #             store_available_object[key] = available_app[key]
        #             pre_processing_dict['availableApps'].append(store_available_object)
            
    return JsonResponse(pre_processing_dict)

 
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

    breakpoint()
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
    breakpoint()
    context = {
        'availableApps': available_apps,
        'installedApps': installed_apps + github_apps,
        'incompatibleApps': incompatible_apps,
        'tethysVersion': tethys_version_regex,
    }

    return JsonResponse(context)
