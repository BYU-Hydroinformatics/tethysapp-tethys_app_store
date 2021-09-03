import shutil
from datetime import datetime
import tempfile
import os
import requests, json
from .user_settings import *

from .hydrogate import HydroDS
from .model_parameters_list import file_contents_dict


def hydrods_model_input_service_single_call(hs_client_id, hs_client_secret, token, hydrods_name, hydrods_password,
                                            hs_name, hs_password,
                                 topY, bottomY, leftX, rightX,
                                lat_outlet, lon_outlet, streamThreshold, watershedName,
                                epsgCode, startDateTime, endDateTime, dx, dy, dxRes, dyRes,
                                usic, wsic, tic, wcic, ts_last,
                                res_title, res_keywords,
                                 **kwargs):

    service_response = {
        'status': 'Error',
        'result': 'Failed to make the HydroDS request.'
    }

    try:
        url = 'http://129.123.41.218:20199/api/dataservice/createuebinput'  # TODO: change to production server link
        auth = (hydrods_name, hydrods_password)  # TODO: change to production account info
        payload = {
            'hs_username': hs_name,
            'hs_password': hs_password,
            'hs_client_id': hs_client_id,
            'hs_client_secret': hs_client_secret,
            'token': token,
            'hydrods_name': hydrods_name,
            'hydrods_password': hydrods_password,
            'topY': topY,
            'bottomY': bottomY,
            'leftX': leftX,
            'rightX': rightX,
            # 'lat_outlet': lat_outlet,
            # 'lon_outlet': lon_outlet,
            'streamThreshold': streamThreshold,
            'watershedName': watershedName,
            'epsgCode': epsgCode,
            'startDateTime': startDateTime,
            'endDateTime': endDateTime,
            'dx': dx,
            'dy': dy,
            'dxRes': dxRes,
            'dyRes': dyRes,
            'usic': usic,
            'wsic': wsic,
            'tic': tic,
            'wcic': wcic,
            'ts_last': ts_last,
            'res_title': res_title,
            'res_keywords': json.dumps(res_keywords.split(',')),
        }

        if lat_outlet and lon_outlet:
            payload['lat_outlet'] = lat_outlet
            payload['lon_outlet'] = lon_outlet

        response = requests.get(url, params=payload, auth=auth)
        response_dict = json.loads(response.text)

        if response.status_code == 200:
            if response_dict['error']:
                service_response['result'] = format(response_dict['error'])
            elif response_dict['data']['info']:
                service_response['status'] = 'Success'
                service_response['result'] = response_dict['data']['info']
        else:
            service_response['result'] = 'Failed to run HydroDS web service for model inputs preparation.'
    except Exception:
        pass

    return service_response



def hydrods_model_input_service(hs_name, hs_password, hydrods_name, hydrods_password, topY, bottomY, leftX, rightX,
                                lat_outlet, lon_outlet, streamThreshold, watershedName,
                                epsgCode, startDateTime, endDateTime, dx, dy, dxRes, dyRes,
                                usic, wsic, tic,wcic, ts_last,
                                res_title, res_keywords,
                                 **kwargs):

    # TODO: pass the HydroShare user token, client id, client secret not the user name and password
    service_response = {
        'status': 'Success',
        'result': 'The model input has been shared in HydroShare'
    }

    # Authentication
    try:
        HDS = HydroDS(username=hydrods_name, password=hydrods_password)
        for item in HDS.list_my_files():
            try:
                HDS.delete_my_file(item.split('/')[-1])

            except Exception as e:
                continue

    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Please provide the correct user name and password to use HydroDS web services.' + e.message
        return service_response
    # TODO: create new folder for new job


    # prepare watershed DEM data
    try:
        input_static_DEM  = 'nedWesternUS.tif'
        subsetDEM_request = HDS.subset_raster(input_raster=input_static_DEM, left=leftX, top=topY, right=rightX,
                                          bottom=bottomY, output_raster=watershedName + 'DEM84.tif')

        #Options for projection with epsg full list at: http://spatialreference.org/ref/epsg/
        myWatershedDEM = watershedName + 'Proj' + str(dx) + '.tif'
        WatershedDEM = HDS.project_resample_raster(input_raster_url_path=subsetDEM_request['output_raster'],
                                                          cell_size_dx=dx, cell_size_dy=dy, epsg_code=epsgCode,
                                                          output_raster=myWatershedDEM, resample='bilinear')

        outlet_shapefile_result = HDS.create_outlet_shapefile(point_x=lon_outlet, point_y=lat_outlet,
                                                          output_shape_file_name=watershedName+'Outlet.shp')
        project_shapefile_result = HDS.project_shapefile(outlet_shapefile_result['output_shape_file_name'], watershedName + 'OutletProj.shp',
                                                     epsg_code=epsgCode)

        Watershed_hires = HDS.delineate_watershed(WatershedDEM['output_raster'],
                        input_outlet_shapefile_url_path=project_shapefile_result['output_shape_file'],
                        threshold=streamThreshold, epsg_code=epsgCode,
                        output_raster=watershedName + str(dx) + 'WS.tif',
                        output_outlet_shapefile=watershedName + 'movOutlet.shp')

        #HDS.download_file(file_url_path=Watershed_hires['output_raster'], save_as=workingDir+watershedName+str(dx)+'.tif')

        ####Resample watershed grid to coarser grid
        if dxRes == dx and dyRes == dy:
            Watershed = Watershed_hires
        else:
            Watershed = HDS.resample_raster(input_raster_url_path = Watershed_hires['output_raster'],
                    cell_size_dx=dxRes, cell_size_dy=dyRes, resample='near', output_raster=watershedName + str(dxRes) + 'WS.tif')

        #HDS.download_file(file_url_path=Watershed['output_raster'], save_as=workingDir+watershedName+str(dxRes)+'.tif')

        ##  Convert to netCDF for UEB input
        Watershed_temp = HDS.raster_to_netcdf(Watershed['output_raster'], output_netcdf='watershed'+str(dxRes)+'.nc')

        # In the netCDF file rename the generic variable "Band1" to "watershed"
        Watershed_NC = HDS.netcdf_rename_variable(input_netcdf_url_path=Watershed_temp['output_netcdf'],
                                    output_netcdf='watershed.nc', input_variable_name='Band1', output_variable_name='watershed')
    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Failed to prepare the watershed DEM data.'+ e.message
        # TODO clean up the space
        return service_response



    # prepare the terrain variables
    try:
        # aspect
        aspect_hires = HDS.create_raster_aspect(input_raster_url_path=WatershedDEM['output_raster'],
                                    output_raster=watershedName + 'Aspect' + str(dx)+ '.tif')

        if dx == dxRes and dy == dyRes:
            aspect = aspect_hires
        else:
            aspect = HDS.resample_raster(input_raster_url_path= aspect_hires['output_raster'], cell_size_dx=dxRes,
                                    cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Aspect' + str(dxRes) + '.tif')
        aspect_temp = HDS.raster_to_netcdf(input_raster_url_path=aspect['output_raster'],output_netcdf='aspect'+str(dxRes)+'.nc')
        aspect_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=aspect_temp['output_netcdf'],
                                    output_netcdf='aspect.nc', input_variable_name='Band1', output_variable_name='aspect')
        # slope
        slope_hires = HDS.create_raster_slope(input_raster_url_path=WatershedDEM['output_raster'],
                                    output_raster=watershedName + 'Slope' + str(dx) + '.tif')

        if dx == dxRes and dy == dyRes:
            slope = slope_hires
        else:
            slope = HDS.resample_raster(input_raster_url_path= slope_hires['output_raster'], cell_size_dx=dxRes,
                                    cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Slope' + str(dxRes) + '.tif')
        slope_temp = HDS.raster_to_netcdf(input_raster_url_path=slope['output_raster'], output_netcdf='slope'+str(dxRes)+'.nc')
        slope_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=slope_temp['output_netcdf'],
                                    output_netcdf='slope.nc', input_variable_name='Band1', output_variable_name='slope')

        #Land cover variables
        nlcd_raster_resource = 'nlcd2011CONUS.tif'
        subset_NLCD_result = HDS.project_clip_raster(input_raster=nlcd_raster_resource,
                                    ref_raster_url_path=Watershed['output_raster'],
                                    output_raster=watershedName + 'nlcdProj' + str(dxRes) + '.tif')
        #cc
        nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
                                    variable_name='cc', output_netcdf=watershedName+str(dxRes)+'cc.nc')
        cc_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
                                    output_netcdf='cc.nc', input_variable_name='Band1', output_variable_name='cc')
        #hcan
        nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
                                    variable_name='hcan', output_netcdf=watershedName+str(dxRes)+'hcan.nc')
        hcan_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
                                    output_netcdf='hcan.nc', input_variable_name='Band1',output_variable_name='hcan')
        #lai
        nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
                                    variable_name='lai', output_netcdf=watershedName+str(dxRes)+'lai.nc')
        lai_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
                                    output_netcdf='lai.nc', input_variable_name='Band1',output_variable_name='lai')

    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Failed to prepare the terrain variables.' + e.message
        # TODO clean up the space
        return service_response


    # prepare the climate variables
    try:
        startYear = datetime.strptime(startDateTime,"%Y/%m/%d").year
        endYear = datetime.strptime(endDateTime,"%Y/%m/%d").year
        #### we are using data from Daymet; so data are daily
        startDate = datetime.strptime(startDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')
        endDate = datetime.strptime(endDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')

        climate_Vars = ['vp', 'tmin', 'tmax', 'srad', 'prcp']
        ####iterate through climate variables
        for var in climate_Vars:
            for year in range(startYear, endYear + 1):
                climatestaticFile1 = var + "_" + str(year) + ".nc4"
                climateFile1 = watershedName + '_' + var + "_" + str(year) + ".nc"
                Year1sub_request = HDS.subset_netcdf(input_netcdf=climatestaticFile1,
                                                     ref_raster_url_path=Watershed['output_raster'],
                                                     output_netcdf=climateFile1)
                concatFile = "conc_" + climateFile1
                if year == startYear:
                    concatFile1_url = Year1sub_request['output_netcdf']
                else:
                    concatFile2_url = Year1sub_request['output_netcdf']
                    concateNC_request = HDS.concatenate_netcdf(input_netcdf1_url_path=concatFile1_url,
                                                               input_netcdf2_url_path=concatFile2_url,
                                                               output_netcdf=concatFile)
                    concatFile1_url = concateNC_request['output_netcdf']

            timesubFile = "tSub_" + climateFile1
            subset_NC_by_time_result = HDS.subset_netcdf_by_time(input_netcdf_url_path=concatFile1_url,
                                                                 time_dimension_name='time', start_date=startDate,
                                                                 end_date=endDate, output_netcdf=timesubFile)
            subset_NC_by_time_file_url = subset_NC_by_time_result['output_netcdf']
            if var == 'prcp':
                proj_resample_file = var + "_0.nc"
            else:
                proj_resample_file = var + "0.nc"
            ncProj_resample_result = HDS.project_subset_resample_netcdf(
                input_netcdf_url_path=subset_NC_by_time_file_url,
                ref_netcdf_url_path=Watershed_NC['output_netcdf'],
                variable_name=var, output_netcdf=proj_resample_file)
            ncProj_resample_file_url = ncProj_resample_result['output_netcdf']

            #### Do unit conversion for precipitation (mm/day --> m/hr)
            if var == 'prcp':
                proj_resample_file = var + "0.nc"
                ncProj_resample_result = HDS.convert_netcdf_units(input_netcdf_url_path=ncProj_resample_file_url,
                                                                output_netcdf=proj_resample_file,
                                                                variable_name=var, variable_new_units='m/hr',
                                                                multiplier_factor=0.00004167, offset=0.0)
                # ncProj_resample_file_url = ncProj_resample_result['output_netcdf']

    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Failed to prepare the climate variables.' + e.message
        # TODO clean up the space
        return service_response


    # prepare the parameter files
    try:
        # create temp parameter files
        temp_dir = tempfile.mkdtemp()

        # update the control.dat content
        start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
        end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
        start_str = datetime.strftime(start_obj, '%Y %M %d') + ' 0.0'
        end_str = datetime.strftime(end_obj, '%Y %M %d') + ' 0.0'
        file_contents_dict['control.dat'][8] = start_str
        file_contents_dict['control.dat'][9] = end_str

        # update the siteinitial.dat content
        lat = 0.5 * (topY+bottomY)
        lon = 0.5 * (rightX+leftX)
        file_contents_dict['siteinitial.dat'][45] = str(lat)
        file_contents_dict['siteinitial.dat'][96] = str(lon)

        file_contents_dict['siteinitial.dat'][3] = str(usic)
        file_contents_dict['siteinitial.dat'][6] = str(wsic)
        file_contents_dict['siteinitial.dat'][9] = str(tic)
        file_contents_dict['siteinitial.dat'][12] = str(wcic)
        file_contents_dict['siteinitial.dat'][93] = str(ts_last)

        # write list in parameter files
        for file_name, file_content in file_contents_dict.items():
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, 'w') as para_file:
                para_file.write('\r\n'.join(file_content))  # the line separator is \r\n

        # upload files to Hydro-DS
        for file_name in file_contents_dict.keys():
            HDS.upload_file(file_to_upload=os.path.join(temp_dir, file_name))

        # clean up tempdir
        parameter_file_names = file_contents_dict.keys()
        shutil.rmtree(temp_dir)

    except Exception as e:
        parameter_file_names = []
        shutil.rmtree(temp_dir)


    # share result to HydroShare
    try:
        #upload ueb input package to hydroshare
        ueb_inputPackage_dict = ['watershed.nc', 'aspect.nc', 'slope.nc', 'cc.nc', 'hcan.nc', 'lai.nc',
                                 'vp0.nc', 'srad0.nc', 'tmin0.nc', 'tmax0.nc', 'prcp0.nc']
        HDS.zip_files(files_to_zip=ueb_inputPackage_dict+parameter_file_names, zip_file_name=watershedName+'_input.zip')

        # create resource metadata list
        # TODO create the metadata for ueb model instance: box, time, resolution, watershed name, streamthreshold,epsg code, outlet poi
        hs_title = res_title

        if parameter_file_names:
            hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
                          'The model inputs data files include: {}. The model parameter files include: {}. This model instance resource is complete for model simulation. ' \
                          .format(', '.join(ueb_inputPackage_dict), ', '.join(file_contents_dict.keys()))
        else:
            hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
                          'The prepared files include: {}. This model instance resource still needs model parameter files {}'\
                           .format(', '.join(ueb_inputPackage_dict), ', '.join(file_contents_dict.keys()))

        hs_keywords = res_keywords.split(',')

        metadata = []
        metadata.append({"coverage": {"type": "box",
                                      "value": {"northlimit": str(topY),
                                                "southlimit": str(bottomY),
                                                "eastlimit": str(rightX),
                                                "westlimit": str(leftX),
                                                "units": "Decimal degrees",
                                                "projection": "WGS 84 EPSG:4326"
                                                }
                                      }
                         })

        start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
        end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
        metadata.append({"coverage": {"type": "period",
                                      "value": {"start": datetime.strftime(start_obj, '%M/%d/%Y'),
                                                "end": datetime.strftime(end_obj, '%M/%d/%Y'),
                                                }
                                      }
                         })
        # metadata.append({'contributor': {'name': 'John Smith', 'email': 'jsmith@gmail.com'}})
        # metadata.append({'relation': {'type': 'cites', 'value': 'http'}})

        # create resource
        HDS.set_hydroshare_account(hs_name, hs_password)
        res_info = HDS.create_hydroshare_resource(file_name=watershedName+'_input.zip', resource_type='ModelInstanceResource', title=hs_title,
                                   abstract=hs_abstract, keywords=hs_keywords, metadata=metadata)
    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Failed to share the results to HydroShare.' + e.message
        # TODO clean up the space
        return service_response

    service_response['result'] = "A model instance resource with name '{}' has been created with link https://www.hydroshare.org/resoruce/{}".format(
                                    res_title, res_info['resource_id'])

    return service_response
