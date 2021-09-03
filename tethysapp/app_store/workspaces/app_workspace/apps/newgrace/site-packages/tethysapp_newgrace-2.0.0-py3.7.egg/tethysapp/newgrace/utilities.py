import fiona
from netCDF4 import Dataset
import os
from datetime import datetime, timedelta
import calendar
import numpy as np
import tempfile
import shutil
import sys
import gdal
import ogr
import osr
import requests
import math
import json
import functools
import shapely.geometry  # Need this to find the bounds of a given geometry
import shapely.ops
import geojson
import pyproj
from pyproj import Proj, transform
from .config import get_global_netcdf_dir
from hs_restclient import HydroShare


def get_global_dates():
    grace_layer_options = []
    grace_nc = get_global_netcdf_dir()+'GRC_jpl_tot.nc'
    # for file in os.listdir(GLOBAL_DIR):
    #     if file.startswith('GRC') and file.endswith('.nc'):
    #         grace_nc = GLOBAL_DIR + file

    start_date = '01/01/2002:00:00:00'

    nc_fid = Dataset(grace_nc, 'r')  # Reading the netcdf file
    nc_var = nc_fid.variables  # Get the netCDF variables
    list(nc_var.keys())  # Getting variable keys

    time = nc_var['time'][:]

    date_str = datetime.strptime(start_date, "%m/%d/%Y:%H:%M:%S")  # Start Date string.

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the index of the current timestep

        end_date = date_str + timedelta(days=float(v))  # Actual human readable date of the timestep

        ts_file_name = end_date.strftime("%Y-%m-%d:%H:%M:%S")  # Changing the date string format
        ts_display = end_date.strftime("%Y %B %d")
        grace_layer_options.append([ts_display, ts_file_name])

    return grace_layer_options


def user_permission_test(user):
    return user.is_superuser or user.is_staff


def get_global_plot_api(pt_coords, start_date, end_date, GLOBAL_NC):

    graph_json = {}

    ts_plot = []

    nc_file = GLOBAL_NC

    coords = pt_coords.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])
    if stn_lon < 0.0:
        stnd_lon = float(stn_lon+360.0)
    else:
        stnd_lon = stn_lon

    nc_fid = Dataset(nc_file, 'r')
    nc_var = nc_fid.variables  # Get the netCDF variables
    list(nc_var.keys())  # Getting variable keys

    time = nc_var['time'][:]
    start_date = '2002-01-01'
    date_str = datetime.strptime(start_date, "%Y-%m-%d")  # Start Date string.
    lat = nc_var['lat'][:]
    lon = nc_var['lon'][:]

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the index of the current timestep

        actual_date = date_str + timedelta(days=float(v))  # Actual human readable date of the timestep

        data = nc_var['lwe_thickness'][timestep, :, :]

        lon_idx = (np.abs(lon - stnd_lon)).argmin()
        lat_idx = (np.abs(lat - stn_lat)).argmin()

        value = data[lat_idx, lon_idx]

        time_stamp = calendar.timegm(actual_date.utctimetuple()) * 1000
        if start_date < str(actual_date) < end_date:
            ts_plot.append([time_stamp, round(float(value), 3)])
            ts_plot.sort()

    graph_json["values"] = ts_plot
    graph_json["point"] = [round(stn_lat, 2), round(stn_lon, 2)]
    graph_json = json.dumps(graph_json)

    return graph_json


def get_pt_region(pt_coords, nc_file):

    graph_json = {}
    ts_plot = []
    ts_plot_int = []

    coords = pt_coords.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])
    if stn_lon < 0.0:
        stnd_lon = float(stn_lon+360.0)
    else:
        stnd_lon = stn_lon

    nc_fid = Dataset(nc_file, 'r')
    nc_var = nc_fid.variables  # Get the netCDF variables
    list(nc_var.keys())  # Getting variable keys

    time = nc_var['time'][:]
    start_date = '01/01/2002'
    date_str = datetime.strptime(start_date, "%m/%d/%Y")  # Start Date string.
    lat = nc_var['lat'][:]
    lon = nc_var['lon'][:]

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the index of the current timestep

        end_date = date_str + timedelta(days=float(v))  # Actual human readable date of the timestep

        data = nc_var['lwe_thickness'][timestep, :, :]

        lon_idx = (np.abs(lon - stnd_lon)).argmin()
        lat_idx = (np.abs(lat - stn_lat)).argmin()

        if timestep == 0:
            init_value = data[lat_idx, lon_idx]
        else:
            init_value = init_value

        value = data[lat_idx, lon_idx]

        difference_data_value = (value - init_value) * 0.01 * 6371000 * math.radians(0.25) * \
            6371000 * math.radians(0.25) * abs(math.cos(math.radians(lat_idx))) * 0.000810714

        time_stamp = calendar.timegm(end_date.utctimetuple()) * 1000

        ts_plot_int.append([time_stamp, round(float(difference_data_value), 3)])
        ts_plot_int.sort()

        ts_plot.append([time_stamp, round(float(value), 3)])
        ts_plot.sort()

    graph_json["values"] = ts_plot
    graph_json["integr_values"] = ts_plot_int
    graph_json["point"] = [round(stn_lat, 2), round(stn_lon, 2)]
    graph_json = json.dumps(graph_json)

    return graph_json


def get_global_plot(pt_coords, global_netc):
    graph_json = {}

    ts_plot = []
    ts_plot_int = []
    nc_file = global_netc

    coords = pt_coords.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])
    if stn_lon < 0.0:
        stnd_lon = float(stn_lon+360.0)
    else:
        stnd_lon = stn_lon

    nc_fid = Dataset(nc_file, 'r')
    nc_var = nc_fid.variables  # Get the netCDF variables
    list(nc_var.keys())  # Getting variable keys

    time = nc_var['time'][:]
    start_date = '01/01/2002'
    date_str = datetime.strptime(start_date, "%m/%d/%Y")  # Start Date string.
    lat = nc_var['lat'][:]
    lon = nc_var['lon'][:]

    for timestep, v in enumerate(time):
        current_time_step = nc_var['lwe_thickness'][timestep, :, :]  # Getting the index of the current timestep

        end_date = date_str + timedelta(days=float(v))  # Actual human readable date of the timestep

        data = nc_var['lwe_thickness'][timestep, :, :]

        timestep2 = timestep - 1

        data2 = nc_var['lwe_thickness'][timestep2, :, :]

        # if data.any==float('nan'):
        #     print('its bad')

        lon_idx = (np.abs(lon - stnd_lon)).argmin()
        lat_idx = (np.abs(lat - stn_lat)).argmin()

        if timestep == 0:
            init_value = data[lat_idx, lon_idx]
        else:
            init_value = init_value

        value = data[lat_idx, lon_idx]

        difference_data_value = (value - init_value) * 0.01 * 6371000 * math.radians(0.25) * \
            6371000 * math.radians(0.25) * abs(math.cos(math.radians(lat_idx))) * 0.000810714

        time_stamp = calendar.timegm(end_date.utctimetuple()) * 1000

        ts_plot_int.append([time_stamp, round(float(difference_data_value), 3)])
        ts_plot_int.sort()

        ts_plot.append([time_stamp, round(float(value), 3)])
        ts_plot.sort()

    graph_json["values"] = ts_plot
    graph_json["integr_values"] = ts_plot_int
    graph_json["point"] = [round(stn_lat, 2), round(stn_lon, 2)]
    graph_json = json.dumps(graph_json)
    return graph_json
