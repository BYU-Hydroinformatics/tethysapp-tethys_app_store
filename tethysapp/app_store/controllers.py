from django.http import JsonResponse
from django.shortcuts import render
from tethys_sdk.routing import controller

import json

from .notifications import *
from .resource_helpers import fetch_resources
from .helpers import logger, get_github_install_metadata
from .model import *
from .git_install_handlers import run_git_install, get_status, get_logs, run_git_install_override, get_logs_override, get_status_override
from .scaffold_handler import scaffold_command
from .submission_handlers import run_submit_nursery_app

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

    for resource in all_resources:
        if resource["installed"]:
            installed_apps.append(resource)
        else:
            available_apps.append(resource)

    # Get any apps installed via GitHub install process
    github_apps = get_github_install_metadata(app_workspace)

    context = {
        'availableApps': available_apps,
        'installedApps': installed_apps + github_apps
    }

    return JsonResponse(context)
