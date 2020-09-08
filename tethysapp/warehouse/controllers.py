from django.shortcuts import render
from tethys_sdk.permissions import login_required, permission_required
from tethys_sdk.workspaces import app_workspace

import json

from .notifications import *
from .resource_helpers import fetch_resources
from .helpers import logger

ALL_RESOURCES = []
CACHE_KEY = "warehouse_app_resources"


@login_required()
@permission_required('use_warehouse')
@app_workspace
def home(request, app_workspace):

    require_refresh = request.GET.get('refresh', '') == "true"
    all_resources = fetch_resources(app_workspace, require_refresh)

    installed_apps = []
    available_apps = []

    for resource in all_resources:
        if resource["installed"]:

            installed_apps.append(resource)
        else:
            available_apps.append(resource)

    context = {
        'resources': available_apps,
        'resourcesJson': json.dumps(available_apps),
        'installedApps': json.dumps(installed_apps)
    }

    return render(request, 'warehouse/home.html', context)
