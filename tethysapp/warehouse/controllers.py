from django.shortcuts import render
from tethys_sdk.permissions import login_required, permission_required
from tethys_sdk.workspaces import app_workspace
from django.http import JsonResponse

import json

from .notifications import *
from .resource_helpers import fetch_resources
from .helpers import logger
from .model import *

ALL_RESOURCES = []
CACHE_KEY = "warehouse_app_resources"


@login_required()
@permission_required('use_warehouse')
def home(request):
    return render(request, 'warehouse/home.html', {})


@login_required()
@permission_required('use_warehouse')
@app_workspace
def get_resources(request, app_workspace):
    require_refresh = request.GET.get('refresh', '') == "true"
    # Always require refresh
    all_resources = fetch_resources(app_workspace, require_refresh)

    installed_apps = []
    available_apps = []

    for resource in all_resources:
        if resource["installed"]:
            installed_apps.append(resource)
        else:
            available_apps.append(resource)

    context = {
        'availableApps': available_apps,
        'installedApps': installed_apps
    }

    return JsonResponse(context)
