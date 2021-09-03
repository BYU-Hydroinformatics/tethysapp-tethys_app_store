import datetime
import tempfile
import shutil
import os
import traceback
import requests

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from tethys_services.backends.hs_restclient_helper import get_oauth_hs


hs_hostname = "www.hydroshare.org"


def snow_graph(request):
    """
    Controller that will show the snow graph for user-defined lat / lon.
    """
    # default value for lat, lon
    lat = '50'
    lon = '15'

    # Check form data
    # if request.POST and 'geometry' in request.POST:
    #    geom = request.POST['geometry']
    #    data = json.loads(geom)
    #    coords = data['geometries'][0]['coordinates']
    #    lat = coords[0]
    #    lon = coords[1]

    if request.GET:
        lat = request.GET['inputLat']
        lon = request.GET['inputLon']
        numdays = int(request.GET['inputDays'])
        endDate = request.GET['endDate']
        endDate2 = datetime.datetime.strptime(endDate, '%Y-%m-%d')
        startDate2 = (endDate2 - datetime.timedelta(days=numdays)).strftime("%Y-%m-%d")
        zoom = request.GET["zoom"]
        layer = request.GET['layer1']
        zoom1 = request.GET['zoom1']
        level1 = request.GET['level']

        # Make the waterml url query string
        waterml_url = '?start=%s&end=%s&lat=%s&lon=%s&layer=%s&level=%s&zoom=%s' % (
            startDate2, endDate, lat, lon, layer, zoom1, level1)

        # Make the map url query string
        map_url = '?days=%s&end=%s&lat=%s&lon=%s&zoom=%s' % (numdays, endDate, lat, lon, zoom)

    # Create template context dictionary
    context = {'layer1': layer, 'zoom1': zoom1, 'level1': level1, 'lat': lat, 'lon': lon,
               'startDate': startDate2, 'endDate': endDate, 'waterml_url': waterml_url, 'map_url': map_url}

    return render(request, 'snow_inspector/snow_graph.html', context)


def upload_to_hydroshare(request):
    print("running upload_to_hydroshare!")
    temp_dir = None
    try:
        return_json = {}
        if request.method == 'GET':
            get_data = request.GET

            base_url = request.build_absolute_uri()
            waterml_url = base_url.replace('upload-to-hydroshare', 'waterml')
            print(waterml_url)

            r_title = request.GET['title']
            r_abstract = request.GET['abstract']
            r_keywords_raw = request.GET['keywords']
            r_type = 'CompositeResource'
            r_keywords = r_keywords_raw.split(',')

            #hs = getOAuthHS(request)

            hs = get_oauth_hs(request)

            # download the kml file to a temp directory
            temp_dir = tempfile.mkdtemp()

            waterml_file_path = os.path.join(temp_dir, "snow.wml")
            print(waterml_file_path)

            with open(waterml_file_path, 'w') as f:
                resp = requests.get(waterml_url, verify=False)
                f.write(resp.content)

            # upload the temp file to HydroShare
            if os.path.exists(waterml_file_path):
                resource_id = hs.createResource(r_type, r_title, resource_file=waterml_file_path,
                                                keywords=r_keywords, abstract=r_abstract)
                return_json['success'] = 'File uploaded successfully!'
                return_json['newResource'] = resource_id
            else:
                raise

    except ObjectDoesNotExist as e:
        print((str(e)))
        return_json['error'] = 'Object doesn"t exist: Login timed out! Please re-sign in with your HydroShare account.'
    except TokenExpiredError as e:
        print((str(e)))
        return_json['error'] = 'Login timed out! Please re-sign in with your HydroShare account.'
    except Exception as err:
        if "401 Unauthorized" in str(err):
            return_json['error'] = 'Username or password invalid.'
        elif "400 Bad Request" in str(err):
            return_json['error'] = 'File uploaded successfully despite 400 Bad Request Error.'
        else:
            traceback.print_exc()
            return_json['error'] = 'HydroShare rejected the upload for some reason.'
    finally:
        if temp_dir != None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        print(return_json)
    return JsonResponse(return_json)
