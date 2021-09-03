from django.http import JsonResponse
from .utilities import *
import json
from .config import *


def api_get_point_values(request):
    json_obj = {}

    if request.method == 'GET' and 'start_date' in request.GET:

        latitude = None
        longitude = None
        signal_solution = None
        storage_type = None
        start_date = None
        end_date = None

        if request.GET.get('latitude'):
            latitude = request.GET['latitude']
        if request.GET.get('longitude'):
            longitude = request.GET['longitude']

        if request.GET.get('signal_solution'):
            signal_solution = request.GET['signal_solution']

        if request.GET.get('storage_type'):
            storage_type = request.GET['storage_type']

        if request.GET.get('start_date'):
            start_date = request.GET['start_date']
        if request.GET.get('end_date'):
            end_date = request.GET['end_date']

        coords = str(longitude) + ',' + str(latitude)

        GLOBAL_NC = get_global_netcdf_dir()+'GRC_'+signal_solution+'_'+storage_type+'.nc'

        try:
            graph = get_global_plot_api(coords, start_date, end_date, GLOBAL_NC, signal_solution, storage_type)
            graph = json.loads(graph)
            json_obj = graph

            return JsonResponse(json_obj)  # Return the json object with a list of the time and corresponding values

        except:
            json_obj = {
                "Error": "Error Processing Request"}  # Show an error if there are any problems executing the script.

            return JsonResponse(json_obj)
    else:

        latitude = None
        longitude = None
        signal_solution = None
        storage_type = None
        start_date = '2002January1'
        end_date = '2020January1'

        if request.GET.get('latitude'):
            latitude = request.GET['latitude']
        if request.GET.get('longitude'):
            longitude = request.GET['longitude']

        if request.GET.get('signal_solution'):
            signal_solution = request.GET['signal_solution']
        if request.GET.get('storage_type'):
            storage_type = request.GET['storage_type']

        coords = str(longitude) + ',' + str(latitude)

        GLOBAL_NC = get_global_netcdf_dir()+'GRC_'+signal_solution+'_'+storage_type+'.nc'

        try:
            graph = get_global_plot_api(coords, start_date, end_date, GLOBAL_NC)
            graph = json.loads(graph)
            json_obj = graph

            return JsonResponse(json_obj)  # Return the json object with a list of the time and corresponding values

        except:
            json_obj = {
                "Error": "Error Processing Request"}  # Show an error if there are any problems executing the script.

            return JsonResponse(json_obj)
