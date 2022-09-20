import re
import semver
from tethys_portal import __version__ as tethys_version
from django.http import JsonResponse
from django.shortcuts import render
from tethys_sdk.routing import controller

import copy

from .resource_helpers import fetch_resources
from .helpers import get_github_install_metadata

ALL_RESOURCES = []
CACHE_KEY = "warehouse_app_resources"


@controller(
    name='home',
    url='app-store',
    permissions_required='use_app_store',
)
def home(request):
    return render(request, 'app_store/home.html', {})


@controller(
    name='get_resources',
    url='app-store/get_resources',
    permissions_required='use_app_store',
    app_workspace=True,
)
def get_resources(request, app_workspace):
    require_refresh = request.GET.get('refresh', '') == "true"
    # Always require refresh
    all_resources = fetch_resources(app_workspace, require_refresh)

    installed_apps = []
    available_apps = []
    incompatible_apps = []

    for resource in all_resources:
        if resource["installed"]:
            installed_apps.append(resource)
        else:
            # tethys_version_regex = '4.0.0'
            tethys_version_regex = re.search(r'([\d.]+[\d])', tethys_version).group(1)

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

    context = {
        'availableApps': available_apps,
        'installedApps': installed_apps + github_apps,
        'incompatibleApps': incompatible_apps,
        'tethysVersion': tethys_version_regex
    }

    return JsonResponse(context)
