from datetime import *
import time
import sys
import os
import shutil
from ftplib import FTP
import logging
import numpy as np
from itertools import groupby
from django.contrib.auth.decorators import login_required, user_passes_test
import tempfile
import shutil
import sys
import calendar
from netCDF4 import Dataset
from .config import get_global_netcdf_dir, SHELL_DIR
from django.http import JsonResponse, HttpResponse, Http404
from .utilities import user_permission_test


@user_passes_test(user_permission_test)
def grcfo_update_check(data):

    tday = datetime.date.today()
    daytoday = tday.ctime()

    print(("The date today is ", tday))
    print(("The date info. is ", daytoday))

    os.system(SHELL_DIR+'check_for_updates.sh '+get_global_netcdf_dir()+'testing/')
    for files in os.walk(get_global_netcdf_dir()+'testing/'):

        # start_date =

        if "GRCFO_JPLEM" in files:
            response = {"update-available": "update-available"}
        else:
            response = {"not-available": "not-available"}

    return JsonResponse(response)


def update_grace_files():
    os.system(SHELL_DIR+'grcfo_download.sh '+get_global_netcdf_dir())
    return JsonResponse({"success": "success"})


def write_gldas_text_file(directory):
    grace_date_st = []
    # grace_nc = get_global_netcdf_dir() + 'temp/'+'GRC_jpl_tot_test.nc'
    grace_nc = directory+'GRCFO_jpl_total.nc'
    start_date = '01/01/2002:00:00'
    nc_fid = Dataset(grace_nc, 'r')  # Reading the netcdf file
    nc_var = nc_fid.variables  # Get netcdf Variables
    list(nc_var.keys())  # Getting Variable Keys

    time = nc_var['time'][:]

    date_str = datetime.strptime(start_date, "%m/%d/%Y:%H:%M")  # Start date String

    f = open(directory+"GLDASlinks.txt", 'w')
    # f = open('/Users/travismcstraw/Downloads/test/GLDASlinks.txt', 'w')

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the Index of the current timestep

        end_date = date_str + timedelta(days=float(v))  # Actual Human readable date of timestep

        ts_file_name = end_date.strftime("%Y%m%d.%H%M")  # Change the date string to match text link download format
        ts_display = end_date.strftime("%Y %B %d")
        year = end_date.strftime("%Y")
        num_days = end_date.timetuple().tm_yday
        if 10 <= num_days < 100:
            num_days = '0'+str(num_days)
        elif num_days < 10:
            num_days = '00'+str(num_days)
        else:
            num_days = str(num_days)

        grace_date_st.append([ts_display, ts_file_name])
        f.write("http://hydro1.gesdisc.eosdis.nasa.gov/daac-bin/OTF/HTTP_services.cgi?FILENAME=%2Fdata%2FGLDAS%2FGLDAS_NOAH025_3H.2.1%2F"+year+"%2F"+num_days+"%2FGLDAS_NOAH025_3H.A"+ts_file_name+".021.nc4&FORMAT=bmM0Lw&BBOX=-60%2C-180%2C90%2C180&LABEL=GLDAS_NOAH025_3H.A"+ts_file_name +
                ".021.nc4.SUB.nc4&SHORTNAME=GLDAS_NOAH025_3H&SERVICE=L34RS_LDAS&VERSION=1.02&DATASET_VERSION=2.1&VARIABLES=CanopInt_inst%2CQs_acc%2CQsb_acc%2CQsm_acc%2CRootMoist_inst%2CSoilMoi0_10cm_inst%2CSoilMoi10_40cm_inst%2CSoilMoi100_200cm_inst%2CSoilMoi40_100cm_inst%2CSWE_inst"+"\n")
    f.close()

    return grace_date_st


def download_gldas_data():
    write_gldas_text_file(get_global_netcdf_dir())
    os.system(SHELL_DIR+'gldas_download_and_update.sh '+get_global_netcdf_dir())
    return JsonResponse({"success": "success"})


def update_other_solution_files():
    os.system(SHELL_DIR+'other_solutions_update.sh '+get_global_netcdf_dir())

    return JsonResponse({"success": "success"})


def get_global_dates():
    grace_layer_options = []
    grace_nc = get_global_netcdf_dir()+'GRC_jpl_tot.nc'
    # for file in os.listdir(GLOBAL_DIR):
    #     if file.startswith('GRC') and file.endswith('.nc'):
    #         grace_nc = GLOBAL_DIR + file

    start_date = '01/01/2002:00:00:00'

    nc_fid = Dataset(grace_nc, 'r')  # Reading the netcdf file
    nc_var = nc_fid.variables  # Get the netCDF variables
    nc_dim = nc_fid.dimensions
    print(nc_dim)

    list(nc_var.keys())  # Getting variable keys

    time = nc_var['time'][:]
    print(time)
    date_str = datetime.strptime(start_date, "%m/%d/%Y:%H:%M:%S")  # Start Date string.

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the index of the current timestep

        end_date = date_str + timedelta(days=float(v))  # Actual human readable date of the timestep

        ts_file_name = end_date.strftime("%Y-%m-%d:%H:%M:%S")  # Changing the date string format
        ts_display = end_date.strftime("%Y %B %d")
        grace_layer_options.append([ts_display, ts_file_name])

    return grace_layer_options


# def download_monthly_gldas_data():
#     os.system(SHELL_DIR+'monthly_gldas_download.sh '+get_global_netcdf_dir()+'temp/'+' gracedata1 '+'GRACEData1')
#
#     return JsonResponse({"success": "success"})
