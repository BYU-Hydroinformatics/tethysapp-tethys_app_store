import json
import math

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError
from tethys_sdk.workspaces import app_workspace
from tethys_sdk.compute import get_scheduler

# get job manager for the app
from .app import Gwlm as app
job_manager = app.get_job_manager()
from .interpolation_utils import process_interpolation
from .model import (Region,
                    Aquifer,
                    Variable,
                    Well)
from .utils import (create_outlier,
                    get_session_obj,
                    user_permission_test,
                    process_region_shapefile,
                    process_aquifer_shapefile,
                    get_shapefile_attributes,
                    get_timeseries,
                    get_well_obs,
                    get_well_info,
                    get_wms_datasets,
                    get_wms_metadata,
                    get_region_aquifers_list,
                    get_region_variables_list,
                    process_wells_file,
                    process_measurements_file)


@user_passes_test(user_permission_test)
@app_workspace
def region_add(request, app_workspace):
    """
    Ajax Controller to process the region shapefile. Submitted through the add_region page.
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_name = info.get('region')

        shapefile = request.FILES.getlist('shapefile')

        response = process_region_shapefile(shapefile, region_name, app_workspace)

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def region_tabulator(request):
    """
    Ajax controller to generate the region tabulator table
    """
    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))
    session = get_session_obj()
    # RESULTS_PER_PAGE = 10
    num_regions = session.query(Region).count()
    last_page = math.ceil(int(num_regions) / int(size))
    data_dict = []

    regions = (session.query(Region).order_by(Region.id)
    [(page * size):((page + 1) * size)])

    for region in regions:
        json_dict = {"id": region.id,
                     "region_name": region.region_name}
        data_dict.append(json_dict)

    session.close()

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def region_update(request):
    """
    Ajax controller to update region values in the edit region page
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = info.get('region_id')
        region_name = info.get('region_name')
        try:
            int(region_id)
        except ValueError:
            return JsonResponse({'error': 'Region id is faulty.'})

        region = session.query(Region).get(region_id)

        try:
            region.region_name = region_name

            session.commit()
            session.close()
            return JsonResponse({'success': "Region successfully updated!"})
        except Exception as e:
            session.close()
            return JsonResponse({'error': "There is a problem with your request. " + str(e)})


@user_passes_test(user_permission_test)
def region_delete(request):
    """
    Ajax controller for deleting a region.
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        region_id = post_info.get('region_id')

        try:
            # delete region
            try:
                region = session.query(Region).get(region_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The region to delete does not exist."})

            session.delete(region)
            session.commit()
            session.close()
            return JsonResponse({'success': "Region successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


@user_passes_test(user_permission_test)
@app_workspace
def aquifer_add(request, app_workspace):
    """
    Ajax controller to add aquifers to a region
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = int(info.get('region_id'))
        name_attr = info.get('name_attribute')
        id_attr = info.get('id_attribute')

        shapefile = request.FILES.getlist('shapefile')

        response = process_aquifer_shapefile(shapefile,
                                             region_id,
                                             name_attr,
                                             id_attr,
                                             app_workspace)

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def aquifer_tabulator(request):
    """
    Ajax controller to generate the aquifer tabulator table
    """
    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))
    session = get_session_obj()
    # RESULTS_PER_PAGE = 10
    num_aquifers = session.query(Aquifer).count()
    last_page = math.ceil(int(num_aquifers) / int(size))
    data_dict = []

    aquifers = (session.query(Aquifer).order_by(Aquifer.id)
    [(page * size):((page + 1) * size)])

    for aquifer in aquifers:
        json_dict = {"id": aquifer.id,
                     "aquifer_id": aquifer.aquifer_id,
                     "aquifer_name": aquifer.aquifer_name}
        data_dict.append(json_dict)

    session.close()

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def aquifer_update(request):
    """
    Ajax controller to update aquifer values in the edit aquifer page
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        aquifer_id = info.get('aquifer_id')
        aquifer_name = info.get('aquifer_name')
        aquifer_name_id = info.get('aquifer_name_id')
        try:
            int(aquifer_id)
        except ValueError:
            return JsonResponse({'error': 'Region id is faulty.'})

        aquifer = session.query(Aquifer).get(aquifer_id)

        try:
            aquifer.aquifer_name = aquifer_name
            aquifer.aquifer_id = aquifer_name_id

            session.commit()
            session.close()
            return JsonResponse({'success': "Aquifer successfully updated!"})
        except Exception as e:
            session.close()
            return JsonResponse({'error': "There is a problem with your request. " + str(e)})


@user_passes_test(user_permission_test)
def aquifer_delete(request):
    """
    Controller for deleting an aquifer through the edit aquifer page.
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        aquifer_id = post_info.get('aquifer_id')

        try:
            # delete point
            try:
                aquifer = session.query(Aquifer).get(aquifer_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The aquifer to delete does not exist."})

            session.delete(aquifer)
            session.commit()
            session.close()
            return JsonResponse({'success': "Aquifer successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


@user_passes_test(user_permission_test)
@app_workspace
def get_shp_attributes(request, app_workspace):
    """
    Ajax controller to get attributes of uploaded aquifer file. Can be shapefile, csv, or geojson.
    """
    if request.is_ajax() and request.method == 'POST':

        try:

            shapefile = request.FILES.getlist('shapefile')

            attributes = get_shapefile_attributes(shapefile, app_workspace, True)

            response = {"success": "success",
                        "attributes": attributes}

            return JsonResponse(response)

        except Exception as e:
            json_obj = {'error': json.dumps(e)}

            return JsonResponse(json_obj)


@user_passes_test(user_permission_test)
@app_workspace
def get_well_attributes(request, app_workspace):
    """
    Ajax controller to get attributes for add wells page
    """
    if request.is_ajax() and request.method == 'POST':

        try:

            shapefile = request.FILES.getlist('shapefile')

            attributes = get_shapefile_attributes(shapefile, app_workspace, False)

            response = {"success": "success",
                        "attributes": attributes}

            return JsonResponse(response)

        except Exception as e:
            json_obj = {'error': json.dumps(e)}

            return JsonResponse(json_obj)


@user_passes_test(user_permission_test)
@app_workspace
def get_measurements_attributes(request, app_workspace):
    """
    Ajax controller to get attributes for add measurements page
    """
    if request.is_ajax() and request.method == 'POST':

        try:

            shapefile = request.FILES.getlist('shapefile')

            attributes = get_shapefile_attributes(shapefile, app_workspace, False)

            response = {"success": "success",
                        "attributes": attributes}

            return JsonResponse(response)

        except Exception as e:
            json_obj = {'error': json.dumps(e)}

            return JsonResponse(json_obj)


@user_passes_test(user_permission_test)
def get_aquifers(request):
    """
    Ajax controller to get list of aquifers in a region
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        region_id = int(info.get('id'))
        aquifers_list = get_region_aquifers_list(region_id)
        variables_list = get_region_variables_list(region_id)

        response = {'success': 'success',
                    'variables_list': variables_list,
                    'aquifers_list': aquifers_list}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def get_wells(request):
    """
    Ajax controller to get wells in a given aquifer
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        aquifer_id = info.get('id')
        session = get_session_obj()
        wells = session.query(Well).filter(Well.aquifer_id == aquifer_id)
        wells_list = [[well.well_name, well.id] for well in wells]
        session.close()

        response = {'success': 'success',
                    'wells_list': wells_list}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
@app_workspace
def wells_add(request, app_workspace):
    """
    Ajax controller to add wells
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        lat = info.get('lat')
        lon = info.get('lon')
        well_id = info.get('id')
        name = info.get('name')
        gse = info.get('gse')
        attributes = info.get('attributes')
        file = request.FILES.getlist('shapefile')
        aquifer_id = info.get('aquifer_id')
        aquifer_col = info.get('aquifer_col')
        region_id = int(info.get('region_id'))
        response = process_wells_file(lat, lon, well_id, name,
                                      gse, attributes, file,
                                      aquifer_id, aquifer_col,
                                      app_workspace, region_id)

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def wells_tabulator(request):
    """
    Ajax controller for the wells tabulator table
    """
    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))
    session = get_session_obj()
    # RESULTS_PER_PAGE = 10
    num_wells = session.query(Well).count()
    last_page = math.ceil(int(num_wells) / int(size))
    data_dict = []

    wells = (session.query(Well).order_by(Well.id)
    [(page * size):((page + 1) * size)])

    for well in wells:
        json_dict = {"id": well.id,
                     "well_name": well.well_name,
                     "gse": well.gse,
                     "attr_dict": json.dumps(well.attr_dict)
                     }
        data_dict.append(json_dict)

    session.close()

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def well_delete(request):
    """
    Controller for deleting a well.
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        well_id = post_info.get('well_id')

        try:
            # delete point
            try:
                well = session.query(Well).get(well_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The well to delete does not exist."})

            session.delete(well)
            session.commit()
            session.close()
            return JsonResponse({'success': "Well successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


@user_passes_test(user_permission_test)
@app_workspace
def measurements_add(request, app_workspace):
    """
    Ajax controller to add measurements to wells
    """
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        file = request.FILES.getlist('shapefile')
        time = info.get("time")
        value = info.get("value")
        well_id = info.get("id")
        variable_id = int(info.get("variable_id"))
        time_format = info.get("date_format")
        region_id = int(info.get("region_id"))
        aquifer_id = info.get('aquifer_id')
        aquifer_col = info.get('aquifer_col')
        response = process_measurements_file(region_id, well_id, time, value,
                                             time_format, variable_id, file,
                                             aquifer_id, aquifer_col,
                                             app_workspace)

        return JsonResponse(response)


def region_timeseries(request):
    """
    Ajax controller to get timeseries for a selected region, well, variable
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST
        well_id = info.get('well_id')
        variable_id = int(info.get('variable_id'))
        timeseries = get_timeseries(well_id, variable_id)
        response['success'] = 'success'
        response['timeseries'] = timeseries
        response['well_info'] = get_well_info(well_id)

        return JsonResponse(response)


def region_well_obs(request):
    """
    Ajax controller to get the observation count for wells for a given aquifer and variable
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST
        aquifer_id = int(info.get('aquifer_id'))
        variable_id = int(info.get('variable_id'))
        well_obs = get_well_obs(aquifer_id, variable_id)
        response['obs_dict'] = well_obs
        if len(well_obs) > 0:
            response['min_obs'] = min(well_obs.values())
            response['max_obs'] = max(well_obs.values())
        response['success'] = 'success'

    return JsonResponse(response)


def set_outlier(request):
    """
    Ajax controller to set outlier
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST
        well_id = info.get('well_id')
        outlier = create_outlier(well_id)
        response['success'] = 'success'
        response['outlier'] = outlier

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def variable_tabulator(request):
    """
    Ajax controller to get variable tabulator table
    """
    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))
    session = get_session_obj()
    # RESULTS_PER_PAGE = 10
    num_vars = session.query(Variable).count()
    last_page = math.ceil(int(num_vars) / int(size))
    data_dict = []

    vars = (session.query(Variable).order_by(Variable.id)
    [(page * size):((page + 1) * size)])

    for var in vars:
        json_dict = {"id": var.id,
                     "variable_name": var.name,
                     "variable_units": var.units,
                     "variable_description": var.description,
                     }
        data_dict.append(json_dict)

    session.close()

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def variable_update(request):
    """
    Ajax controller to update variable values in the edit variable page
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        variable_id = info.get('variable_id')
        variable_name = info.get('variable_name')
        variable_units = info.get('variable_units')
        variable_description = info.get('variable_description')

        try:
            int(variable_id)
        except ValueError:
            return JsonResponse({'error': 'Variable id is faulty.'})

        variable = session.query(Variable).get(variable_id)

        try:
            variable.name = variable_name
            variable.units = variable_units
            variable.description = variable_description

            session.commit()
            session.close()
            return JsonResponse({'success': "Variable successfully updated!"})
        except Exception as e:
            session.close()
            return JsonResponse({'error': "There is a problem with your request. " + str(e)})


@user_passes_test(user_permission_test)
def variable_delete(request):
    """
    Controller for deleting a variable.
    """
    session = get_session_obj()

    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        variable_id = post_info.get('variable_id')

        try:
            # delete point
            try:
                variable = session.query(Variable).get(variable_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The variable to delete does not exist."})

            session.delete(variable)
            session.commit()
            session.close()
            return JsonResponse({'success': "Variable successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


@user_passes_test(user_permission_test)
def interpolate(request):
    """
    Ajax controller to generate the interpolation file
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        try:
            post_info = request.POST
            scheduler = get_scheduler(name='dask_local')

            info_dict = post_info.dict()
            result = process_interpolation(info_dict)
            # from .job_functions import delayed_job
            # #
            # # Create dask delayed object
            # delayed = delayed_job(info_dict)
            # dask = job_manager.create_job(
            #     job_type='DASK',
            #     name='dask_delayed',
            #     user=request.user,
            #     scheduler=scheduler,
            # )
            #
            # # Execute future
            # dask.execute(delayed)
            response['success'] = 'success'
            response['result'] = result
        except Exception as e:
            response['error'] = str(e)

        return JsonResponse(response)


def region_wms_datasets(request):
    """
    Ajax controller to get wms datasets for given region, aquifer
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        aquifer_name = post_info.get('aquifer_name')
        variable_id = post_info.get('variable_id')
        region_id = post_info.get('region_id')
        well_files = get_wms_datasets(aquifer_name, variable_id, region_id)
        response['success'] = 'success'
        response['wms_files'] = well_files

    return JsonResponse(response)


def region_wms_metadata(request):
    """
    Ajax controller to get the min and max for a selected interpolation netcdf file
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        aquifer_name = post_info.get('aquifer_name')
        file_name = post_info.get('file_name')
        region_id = post_info.get('region')
        range_min, range_max = get_wms_metadata(aquifer_name, file_name, region_id)
        response['success'] = 'success'
        response['range_min'] = range_min
        response['range_max'] = range_max
        # response['wms_files'] = well_files

    return JsonResponse(response)
