from django.shortcuts import render
from tethys_sdk.permissions import login_required
from tethys_sdk.workspaces import app_workspace

import json

from .notifications import *
from .resource_helpers import fetch_resources
from .helpers import logger
from .model import *

ALL_RESOURCES = []
CACHE_KEY = "warehouse_app_resources"


@login_required()
@app_workspace
def home(request, app_workspace):

    require_refresh = request.GET.get('refresh', '') == "true"
    all_resources = fetch_resources(app_workspace, require_refresh)

    tag_list = []

    # for resource in ALL_RESOURCES:
    #     resource['tag_class'] = ""
    #     if len(resource['metadata']['app_tags']) > 0:
    #         resource['tag_class'] = ' '.join(resource['metadata']['app_tags'])
    #         tag_list = tag_list + resource['metadata']['app_tags']

    # tag_list = list(set(tag_list))
    context = {'resources': all_resources,
               'resourcesJson': json.dumps(all_resources),
               "tags": tag_list}

    return render(request, 'warehouse/home.html', context)
