from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import Button

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2


# @TODO: Move these to settings that can be configured for the application

hs_client_id = 'EoHBKou1Sdcp69Y06zocwGA9BTKxAEQfEtt6EJ2i'
hs_client_secret = 'p31Osu284qCx2YJDf3tVIAkKTfoSPw0MccDPJ4p3MqfUm6lgPMS8tadKqjiLXqs\
moJixaPIeeYQkVOJkKhIfPlqArsPAp3h24eJvZnGxfwjmcNUREFSy5JUSePn6IOCM'


def home(request):

    auth = HydroShareAuthOAuth2(hs_client_id, hs_client_secret, username='rfun', password='bridgefour')
    hs = HydroShare(auth=auth)
    try:
        for resource in hs.resources(group=120):
            metadata = resource.scimeta.custom
            print(metadata)
    except TokenExpiredError as e:
        print(e)
        hs = HydroShare(auth=auth)
        for resource in hs.resources():
            print(resource)

    context = {}

    return render(request, 'warehouse/home.html', context)
