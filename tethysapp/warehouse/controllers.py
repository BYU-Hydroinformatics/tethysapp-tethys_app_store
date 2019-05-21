from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import Button

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2

import yaml
import os

from .app import Warehouse as app


# @TODO: Move these to settings that can be configured for the application

hs_client_id = 'EoHBKou1Sdcp69Y06zocwGA9BTKxAEQfEtt6EJ2i'
hs_client_secret = 'p31Osu284qCx2YJDf3tVIAkKTfoSPw0MccDPJ4p3MqfUm6lgPMS8tadKqjiLXqs\
moJixaPIeeYQkVOJkKhIfPlqArsPAp3h24eJvZnGxfwjmcNUREFSy5JUSePn6IOCM'

GROUP_ID = 120


def home(request):

    auth = HydroShareAuthOAuth2(hs_client_id, hs_client_secret, username='rfun', password='bridgefour')
    hs = HydroShare(auth=auth)
    try:
        resources = hs.resources(group=GROUP_ID)
    except TokenExpiredError as e:
        hs = HydroShare(auth=auth)
        resources = hs.resources(group=GROUP_ID)

    app_workspace = app.get_app_workspace()
    new_file_path = os.path.join(app_workspace.path, 'warehouse.yml')

    resource_metadata = []

    for resource in resources:
        resource_id = resource['resource_id']

        warehouse_yaml = hs.getResourceFile(resource_id, 'warehouse.yml', destination=app_workspace.path)
        print(resource)
        with open(new_file_path, 'r') as stream:
            try:
                config_file = yaml.safe_load(stream)
                resource_metadata.append({'id': resource_id,
                                          'config': config_file})
            except yaml.YAMLError as exc:
                print(exc)

    print(resource_metadata)
    context = {}

    return render(request, 'warehouse/home.html', context)
