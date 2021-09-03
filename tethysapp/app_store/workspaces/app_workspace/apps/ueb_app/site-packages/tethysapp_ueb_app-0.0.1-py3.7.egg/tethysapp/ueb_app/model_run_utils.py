"""
utility functions for model run service
"""

import shutil
import os
import zipfile
import tempfile
import subprocess
import datetime
import json
import xmltodict
import requests
from .user_settings import *

from .hydrogate import HydroDS
from .model_parameters_list import site_initial_variable_codes, input_vairable_codes


# utils for loading the metadata
def get_model_resource_metadata(hs, res_id):

    model_resource_metadata = dict.fromkeys(
        ['north_lat', 'south_lat', 'east_lon', 'west_lon', 'start_time', 'end_time','outlet_x','outlet_y','epsg_code',
         'cell_x_size', 'cell_y_size'],
        None
    )
    model_resource_metadata['res_id'] = res_id

    try:

        # get metadata xml file and parse as dict
        md_dict = xmltodict.parse(hs.getScienceMetadataRDF(res_id).strip("bln' \\ ")) #remove single quotes and trailing \n


        # retrieve bounding box and time
        cov_dict = md_dict['rdf:RDF']['rdf:Description'][0].get('dc:coverage')
        if cov_dict:
            for item in cov_dict:
                if 'dcterms:box' in item.keys():
                    bounding_box_list = item['dcterms:box']['rdf:value'].split(';')
                    for item in bounding_box_list:
                        if 'northlimit' in item:
                            model_resource_metadata['north_lat'] = item.split('=')[1]
                        elif 'southlimit' in item:
                            model_resource_metadata['south_lat'] = item.split('=')[1]
                        elif 'eastlimit' in item:
                            model_resource_metadata['east_lon'] = item.split('=')[1]
                        elif 'westlimit' in item:
                            model_resource_metadata['west_lon'] = item.split('=')[1]

                elif 'dcterms:period' in item.keys():
                    time_list = item['dcterms:period']['rdf:value'].split(';')
                    for item in time_list:
                        if 'start' in item:
                            start_time = item.split('=')[1]
                            model_resource_metadata['start_time'] = start_time.split('T')[0]
                        elif 'end' in item:
                            end_time = item.split('=')[1]
                            model_resource_metadata['end_time'] = end_time.split('T')[0]

        # retrieve extended metadata
        ext_dict = md_dict['rdf:RDF']['rdf:Description'][0].get('hsterms:extendedMetadata')
        info_dict = {}
        for item in ext_dict:
            key = item['rdf:Description']['hsterms:key'].replace(' ', '_').lower()
            info_dict[key] = item['rdf:Description']['hsterms:value']
        model_resource_metadata['cell_y_size'] = info_dict.get('modeling_resolution_dy_(m)')
        model_resource_metadata['cell_x_size'] = info_dict.get('modeling_resolution_dx_(m)')
        model_resource_metadata['outlet_x'] = info_dict.get('outlet_longitude')
        model_resource_metadata['outlet_y'] = info_dict.get('outlet_latitude')
        model_resource_metadata['epsg_code'] = info_dict.get('epsg_code_for_data')

    except Exception as e:
        import traceback
        traceback.print_exc()

    return model_resource_metadata


## utils for running the model service
def submit_model_run_job_single_call(res_id, OAuthHS):
    model_run_job = {
        'status': 'Error',
        'result': 'Failed to make the HydroDS web service call.'
    }

    try:

        # url = 'http://hydro-ds.uwrl.usu.edu/api/dataservice/runuebmodel'
        url = 'http://129.123.41.218:20199/api/dataservice/runuebmodel'
        auth = (hydrods_name, hydrods_password)
        payload = {'resource_id': res_id,
                   'hs_client_id': OAuthHS['client_id'],
                   'hs_client_secret': OAuthHS['client_secret'],
                   'token': json.dumps(OAuthHS['token']),
                   'hs_username': OAuthHS['user_name']
                   }
        response = requests.get(url, params=payload, auth=auth)
        response_dict = json.loads(response.text)

        if response.status_code == 200:
            if response_dict['error']:
                model_run_job['result'] = response_dict['error']
            elif response_dict['data']['info']:
                model_run_job['status'] = 'Success'
                model_run_job['result'] = response_dict['data']['info']
        else:
            model_run_job['result'] = 'Failed to run HydroDS web service for model execution.'

    except Exception as e:
        model_run_job = {
            'status': 'Error',
            'result': 'Failed to make the HydroDS web service call.'
        }

    return model_run_job


def submit_model_run_job(res_id, OAuthHS, hydrods_name, hydrods_password):
    # TODO: call model run service

    try:
        # authentication
        hs = OAuthHS['hs']
        client = HydroDS(username=hydrods_name, password=hydrods_password)
        
        # clean up the HydroDS space
        for item in client.list_my_files():
            try:
                client.delete_my_file(item.split('/')[-1])

            except Exception as e:
                continue

        # download resource bag
        try:
            temp_dir = tempfile.mkdtemp()
            bag_path = os.path.join(temp_dir, res_id + '.zip')
            res = hs.getResource(res_id)
            with open(bag_path, 'wb') as fd:
                for chunk in res:
                    fd.write(chunk)
            zf = zipfile.ZipFile(bag_path)
            zf.extractall(temp_dir)
            zf.close()
            os.remove(bag_path)
            
        except Exception as e:
            model_run_job = {
                'status': 'Error',
                'result': 'Failed to retrieve the resource content files from HydroShare. '
                          'Please refresh the page and click on the submit button again'
            }

            return model_run_job

        # validate files and run model service
        model_input_folder = os.path.join(temp_dir, res_id, 'data', 'contents')

        if os.path.isdir(model_input_folder):  # the resource contents model input files

            # validate the model input files
            validation = validate_model_input_files(model_input_folder)

            # upload the model input and parameter files to HydroDS
            if validation['is_valid']:
                # copy ueb executable
                ueb_exe_path = r'/home/jamy/ueb/UEBGrid_Parallel_Linuxp/ueb'
                shutil.copy(ueb_exe_path, model_input_folder)

                # run ueb model
                process = subprocess.Popen(['./ueb', 'control.dat'], stdout=subprocess.PIPE, cwd=model_input_folder).wait()

                # check simulation result
                if process == 0:
                    # get point output file
                    output_file_name_list = []
                    model_param_files_dict = validation['result']
                    point_index = 1
                    output_control_contents = model_param_files_dict['output_file']['file_contents']
                    point_num = int(output_control_contents[point_index].split(' ')[0])

                    if point_num != 0:
                        for i in range(point_index+1, point_index+1+point_num):
                            output_file_name_list.append(output_control_contents[i].split(' ')[2])

                    # get netcdf output file
                    netcdf_index = point_index+1+point_num
                    netcdf_num = int(output_control_contents[netcdf_index].split(' ')[0])

                    if netcdf_num != 0:
                        for i in range(netcdf_index+1, netcdf_index+1+netcdf_num):
                            output_file_name_list.append(output_control_contents[i].split(' ')[1])

                    # get aggregation file
                    output_file_name_list.append(model_param_files_dict['control_file']['file_contents'][5].split(' ')[0])

                    # zip all the output files
                    zip_file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") +'output_package.zip'
                    zip_file_path = os.path.join(model_input_folder, zip_file_name)
                    zf = zipfile.ZipFile(zip_file_path, 'w')
                    for file_path in [os.path.join(model_input_folder, file_name) for file_name in output_file_name_list]:
                        if os.path.isfile(file_path):
                            zf.write(file_path,os.path.basename(file_path))
                    zf.close()

                    # Share output package to HydroShare
                    res_list = [res['resource_id'] for res in hs.getResourceList(owner=OAuthHS.get('user_name'), types=["ModelInstanceResource"])]

                    # create a new resource
                    current_dir = os.getcwd()
                    os.chdir(model_input_folder)
                    if res_id in res_list:
                        resource_id = hs.addResourceFile(res_id, zip_file_name)
                    else:
                        rtype = 'ModelInstanceResource'
                        title = 'UEB model simulation output'
                        abstract = 'This resource includes the UEB model simulation output files derived from the model' \
                                   ' instance package http://www.hydroshare.org/resource/{}. The model simulation was conducted ' \
                                   'using the UEB web application http://localhost:8000/apps/ueb-app'.format(res_id)
                        keywords = ('UEB', 'Snowmelt simulation')
                        metadata = [{"source": {'derived_from': 'http://www.hydroshare.org/resource/{}'.format(res_id)}}]
                        resource_id = hs.createResource(rtype, title, resource_file=zip_file_name, keywords=keywords,
                                                        abstract=abstract, metadata=json.dumps(metadata))
                    os.chdir(current_dir)

                    model_run_job = {
                        'status': 'Success',
                        'result': 'The UEB model simualtion is completed. Please check resource http://www.hydroshare.org/resource/{}'.format(resource_id)
                    }

                else:
                    model_run_job = {
                        'status': 'Error',
                        'result': 'Failed to execute the UEB model.'
                    }

            else:
                model_run_job = {
                    'status': 'Error',
                    'result': validation['result']
                }

        else:  # the resource doesn't have files
            model_run_job = {
                'status': 'Error',
                'result': 'No model input data and parameter files is retrieved. Please check the resource files or rerun the model simulation app.'
            }

        # # remove the tempdir
        shutil.rmtree(temp_dir)

    except Exception as e:

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        model_run_job = {
            'status': 'Error',
            'result': 'Failed to run the model execution service.' + e.message
        }

    return model_run_job


def validate_model_input_files(model_input_folder):
    try:
        # move all files from zip and folders in the same model_input_folder level
        model_files_path_list = move_files_to_folder(model_input_folder)

        if model_files_path_list:

            # check model parameter files:
            validation = validate_param_files(model_input_folder)

            # check the data input files:
            if validation['is_valid']:
                validation = validate_data_files(model_input_folder, validation['result'])
        else:
            validation = {
                'is_valid': False,
                'result': 'Failed to unpack the model instance resource for file validation.'
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model input files before submitting the model execution job. ' + e.message
        }

    return validation


def move_files_to_folder(model_input_folder):
    """
    move all the files in sub-folder or zip file to the given folder level and remove the zip and sub-folders
    Return the new file path list in the folder
    """
    try:
        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

        while model_files_path_list:
            added_files_list = []

            for model_file_path in model_files_path_list:

                if os.path.isfile(model_file_path) and os.path.splitext(model_file_path)[1] == '.zip':
                    zf = zipfile.ZipFile(model_file_path, 'r')
                    zf.extractall(model_input_folder)
                    extract_file_names = zf.namelist()
                    added_files_list += [os.path.join(model_input_folder, name) for name in extract_file_names]
                    zf.close()
                    os.remove(model_file_path)

                elif os.path.isdir(model_file_path):
                    for dirpath, _, filenames in os.walk(model_file_path):
                        for name in filenames:
                            sub_file_path = os.path.abspath(os.path.join(dirpath, name))
                            new_file_path = os.path.join(model_input_folder, name)
                            shutil.move(sub_file_path, new_file_path)
                            added_files_list.append(new_file_path)
                    shutil.rmtree(model_file_path)

            model_files_path_list = added_files_list

        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

    except Exception as e:
        model_files_path_list = []

    return model_files_path_list


def validate_param_files(model_input_folder):
    try:

        if 'control.dat' in os.listdir(model_input_folder):

            # get the control file path and contents
            file_path = os.path.join(model_input_folder, 'control.dat')
            with open(file_path) as para_file:
                file_contents = [line.replace('\r\n', '').replace('\n', '').replace('\t', ' ') for line in para_file.readlines()]  # remember the repalce symble is '\r\n'. otherwise, it fails to recoganize the parameter file names

            param_files_dict = {
                'control_file': {'file_path': file_path,
                                 'file_contents': file_contents
                                 }
            }

            # get the other model parameter files path and contents
            file_types = ['param_file', 'site_file', 'input_file', 'output_file']
            missing_file_names = []

            for index in range(0, len(file_types)):
                content_index = index + 1
                file_name = param_files_dict['control_file']['file_contents'][content_index]
                file_path = os.path.join(model_input_folder, file_name)

                if file_name in os.listdir(model_input_folder):
                    param_files_dict[file_types[index]] = {'file_path': file_path}

                    with open(file_path) as para_file:
                        file_contents = [line.replace('\r\n', '').replace('\n', '') for line in para_file.readlines()]

                    param_files_dict[file_types[index]]['file_contents'] = file_contents
                else:
                    missing_file_names.append(file_name)

            if missing_file_names:
                validation = {
                    'is_valid': False,
                    'result': 'Please provide the missing model parameter files: {}.'.format(','.join(missing_file_names))
                }
            else:
                validation = {
                    'is_valid': True,
                    'result': param_files_dict
                }
        else:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model parameter file: control.dat.'
            }

    except Exception as e:
        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model parameter files. ' + e.message
        }

    return validation


def validate_data_files(model_input_folder, model_param_files_dict):
    missing_file_names = []

    try:
        # check the control.dat watershed.nc
        watershed_name = model_param_files_dict['control_file']['file_contents'][6]
        if watershed_name not in os.listdir(model_input_folder):
            missing_file_names.append(watershed_name)

        # check the missing files in siteinitial.dat
        site_file_names = []

        for var_name in site_initial_variable_codes:
            for index, content in enumerate(model_param_files_dict['site_file']['file_contents']):
                if var_name in content and model_param_files_dict['site_file']['file_contents'][index+1][0] == '1':
                    site_file_names.append(model_param_files_dict['site_file']['file_contents'][index+2].split(' ')[0])
                    break

        if site_file_names:
            for name in site_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        # check the missing files in inputcontrol.dat
        input_file_names = []
        for var_name in input_vairable_codes:
            for index, content in enumerate(model_param_files_dict['input_file']['file_contents']):
                if var_name in content:
                    if model_param_files_dict['input_file']['file_contents'][index+1][0] == '1':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index+2].split(' ')[0]+'0.nc')
                    elif model_param_files_dict['input_file']['file_contents'][index+1][0] == '0':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index + 2].split(' ')[0])
                    break

        if input_file_names:
            for name in input_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        if missing_file_names:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model input data files: {}'.format(',\n'.join(missing_file_names))
            }
        else:
            validation = {
                'is_valid': True,
                'result': model_param_files_dict
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result':  'Failed to validate the model input data files.' + e.message
        }

    return validation
