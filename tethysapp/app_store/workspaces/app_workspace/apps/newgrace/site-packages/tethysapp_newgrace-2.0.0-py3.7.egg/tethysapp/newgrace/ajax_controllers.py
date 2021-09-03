from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from tethys_sdk.gizmos import *
from .utilities import *
import json
import time
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.exc import IntegrityError
from .model import *
import requests
import urllib.parse
import shapely.geometry
import os
from .app import *
from .config import get_global_netcdf_dir
from .SHAZAAM import *
from .utilities import *


def get_plot_global(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        # Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST["geom_data"]
        storage_type = request.POST['storage_type']
        signal_process = request.POST['signal_process']

        GLOBAL_DIR = os.path.join(get_global_netcdf_dir(), '')

        gbyos_grc_ncf = GLOBAL_DIR + 'GRC_'+signal_process+'_'+storage_type+'.nc'

        # grc_tot_nfc = GLOBAL_DIR + 'GRC_'+signal_process+'_tot.nc'
        # grc_sw_nfc = GLOBAL_DIR + 'GRC_'+signal_process+'_sw.nc'
        # grc_soil_nfc = GLOBAL_DIR + 'GRC_'+signal_process+'_soil.nc'
        # grc_gw_nfc = GLOBAL_DIR + 'GRC_'+signal_process+'_gw.nc'
        #
        # graph_tot = get_global_plot(pt_coords,grc_tot_nfc)
        # graph_tot = json.loads(graph_tot)
        # return_obj["tot_values"] = graph_tot["values"]
        # return_obj["location"] = graph_tot["point"]
        #
        # graph_sw = get_global_plot(pt_coords,grc_sw_nfc)
        # graph_sw = json.loads(graph_sw)
        # return_obj["sw_values"] = graph_sw["values"]
        #
        # graph_soil = get_global_plot(pt_coords,grc_soil_nfc)
        # graph_soil = json.loads(graph_soil)
        # return_obj["soil_values"] = graph_soil["values"]
        #
        # graph_gw = get_global_plot(pt_coords,grc_gw_nfc)
        # graph_gw = json.loads(graph_gw)
        # return_obj["gw_values"] = graph_gw["values"]

        graph = get_global_plot(pt_coords, gbyos_grc_ncf)
        graph = json.loads(graph)
        return_obj["values"] = graph["values"]
        return_obj["integr_values"] = graph["integr_values"]
        return_obj["location"] = graph["point"]

        return_obj['success'] = "success"

    return JsonResponse(return_obj)


def get_plot_reg_pt(request):
    return_obj = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        display_name = request.POST['region_dis_name']
        pt_coords = request.POST['geom_data']
        storage_type = request.POST['storage_type']
        signal_solution = request.POST['signal_process']

        # Session = Newgrace.get_persistent_store_database('grace_db', as_sessionmaker=True)
        # session = Session()

        # region = session.query(Region).get(region_id)
        # display_name = region.display_name
        region_store = ''.join(display_name.split()).lower()

        GLOBAL_DIR = os.path.join(get_global_netcdf_dir(), '')

        # FILE_DIR = os.path.join(GLOBAL_DIR, '')

        # region_dir = os.path.join(FILE_DIR + region_store, '')

        # nc_file = os.path.join(region_dir+region_store+"_"+signal_solution+"_"+storage_type+".nc")
        nc_file = GLOBAL_DIR + 'GRC_' + signal_solution + '_' + storage_type + '.nc'

        if pt_coords:
            graph = get_pt_region(pt_coords, nc_file)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["integr_values"] = graph["integr_values"]
            return_obj["location"] = graph["point"]

        return_obj["success"] = "success"

    return JsonResponse(return_obj)


@user_passes_test(user_permission_test)
def region_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        start_time = time.time()
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        subset2(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)
        end_time = time.time()
        total_time = (end_time - start_time) / 60
        response = {"success": "success"}

        return JsonResponse(response)


#############################################################################################
##                                                                                         ##
##          Chained Subsetting functions see add_region function in add_region.js          ##
##                                                                                         ##
#############################################################################################


@user_passes_test(user_permission_test)
def subset_initial_processing(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_initial(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"initial": "initial"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_jpl_tot(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_jpl_tot(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"jpl-tot": "jpl-tot"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_jpl_gw(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_jpl_gw(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"jpl-gw": "jpl-gw"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_csr_tot(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_csr_tot(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"csr-tot": "csr-tot"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_csr_gw(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_csr_gw(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"csr-gw": "csr-gw"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_gfz_tot(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_gfz_tot(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"gfz-tot": "gfz-tot"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_gfz_gw(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_gfz_gw(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"gfz-gw": "gfz-gw"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_avg_tot(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_avg_tot(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"avg-tot": "avg-tot"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_avg_gw(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_avg_gw(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"avg-gw": "avg-gw"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_sw(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_sw(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"sw": "sw"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_soil(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_soil(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"soil": "soil"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_cleanup(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_file_cleanup(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"cleanup": "cleanup"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def subset_update(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region_name')
        region_store = ''.join(region_name.split()).lower()
        thredds_id = info.get('thredds')

        shapefile = request.FILES.getlist('shapefile')

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        url, uname, pwd = thredds.url, thredds.username, thredds.password

        sub_update_ps(shapefile, region_store, get_global_netcdf_dir(), region_name, thredds_id)

        response = {"success": "success"}

        return JsonResponse(response)


#############################################################################################
##                                                                                         ##
##                              END Chained Subsetting functions                           ##
##                                                                                         ##
#############################################################################################


@user_passes_test(user_permission_test)
def thredds_server_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        thredds_server_name = info.get('thredds_server_name')
        thredds_server_url = info.get('thredds_server_url')
        thredds_server_username = info.get('thredds_server_username')
        thredds_server_password = info.get('thredds_server_password')

        try:
            # cat = Catalog(thredds_url, username=thredds_username, password=thredds_password,disable_ssl_certificate_validation=True)
            # layer_list = cat.get_layers()
            # if layer_list:
            Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
            session = Session()
            thredds_server = Thredds(name=thredds_server_name, url=thredds_server_url,
                                     username=thredds_server_username, password=thredds_server_password)
            session.add(thredds_server)
            session.commit()
            session.close()
            response = {"data": thredds_server_name, "success": "Success"}
        except Exception as e:
            print(e)
            response = {"error": "Error processing the Thredds Server URL. Please check the url,username and password."}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def thredds_server_update(request):
    """
    Controller for updating a geoserver.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        thredds_id = post_info.get('thredds_server_id')
        thredds_name = post_info.get('thredds_server_name')
        thredds_url = post_info.get('thredds_server_url')
        thredds_username = post_info.get('thredds_server_username')
        thredds_password = post_info.get('thredds_server_password')
        # check data
        if not thredds_id or not thredds_name or not thredds_url or not \
                thredds_username or not thredds_password:
            return JsonResponse({'error': "Missing input data."})
        # make sure id is id
        try:
            int(thredds_id)
        except ValueError:
            return JsonResponse({'error': 'Thredds Server id is faulty.'})

        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()

        thredds = session.query(Thredds).get(thredds_id)
        try:

            thredds.name = thredds_name
            thredds.url = thredds_url
            thredds.username = thredds_username
            thredds.password = thredds_password

            session.commit()
            session.close()
            return JsonResponse({'success': "Thredds Server sucessfully updated!"})
        except:
            return JsonResponse({'error': "A problem with your request exists."})


@user_passes_test(user_permission_test)
def thredds_server_delete(request):
    """
    Controller for deleting a geoserver.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        thredds_id = post_info.get('thredds_server_id')

        # initialize session
        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()
        try:
            # delete geoserver
            try:
                thredds = session.query(Thredds).get(thredds_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The thredds server to delete does not exist."})
            session.delete(thredds)
            session.commit()
            session.close()
        except IntegrityError:
            session.close()
            return JsonResponse(
                {'error': "This thredds server is connected with a region! Must remove region to delete."})
        return JsonResponse({'success': "Thredds Server sucessfully deleted!"})
    return JsonResponse({'error': "A problem with your request exists."})


@user_passes_test(user_permission_test)
def region_delete(request):
    """
    Controller for deleting a region.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        region_id = post_info.get('region_id')

        # initialize session
        Session = Newgrace.get_persistent_store_database('gracefo_db', as_sessionmaker=True)
        session = Session()
        try:
            # delete region
            try:
                region = session.query(Region).get(region_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The geoserver to delete does not exist."})
            display_name = region.display_name
            region_store = ''.join(display_name.split()).lower()
            thredds_id = region.thredds_id
            thredds = session.query(Thredds).get(thredds_id)
            thredds_url = thredds.url
            uname = thredds.username
            pwd = thredds.password

            FILE_DIR = os.path.join(get_global_netcdf_dir(), '')

            region_dir = os.path.join(FILE_DIR + region_store, '')

            session.delete(region)
            session.commit()

            session.close()
        except IntegrityError:
            session.close()
            return JsonResponse(
                {'error': "This thredds is connected with a watershed! Must remove connection to delete."})
        finally:
            # Delete the temporary directory once the geojson string is created
            if region_dir is not None:
                if os.path.exists(region_dir):
                    shutil.rmtree(region_dir)
        return JsonResponse({'success': "Region sucessfully deleted!"})
    return JsonResponse({'error': "A problem with your request exists."})
