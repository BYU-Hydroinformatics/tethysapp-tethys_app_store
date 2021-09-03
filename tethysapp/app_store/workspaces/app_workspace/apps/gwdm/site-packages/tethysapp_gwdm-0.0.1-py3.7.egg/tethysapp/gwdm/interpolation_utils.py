import calendar
import copy
import datetime
import os
import shutil
import tempfile
import time
import urllib
from pathlib import Path
from timeit import default_timer as timer
from urllib import request
from xml.etree import cElementTree as ET

import geopandas as gpd
import gstools as gs
import matplotlib.backends.backend_pdf as plt_pdf
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import pandas as pd
import scipy.interpolate as sci_intrp
import xarray
import rioxarray
from geoalchemy2 import functions as gf2
from scipy import interpolate
from shapely import wkt
from shapely.geometry import mapping

from .app import Gwdm as app
from .model import (Aquifer,
                    Well,
                    Measurement)
from .utils import (get_session_obj,
                    get_region_aquifers_list)

SERVER1 = "https://www.esrl.noaa.gov/psd/thredds/wms/Datasets/dai_pdsi/pdsi.mon.mean.selfcalibrated.nc"
LAYER1 = "pdsi"  # name of data column to be returned
SERVER2 = "https://www.esrl.noaa.gov/psd/thredds/wms/Datasets/cpcsoil/soilw.mon.mean.nc"
LAYER2 = "soilw"  # name of data column to be returned
YEARS = [1, 3, 5, 10]


def smooth(y, box_size):
    """ moving window function using convolution
        y:          1D vector of values
        box_size:   size of the moving window, should be an odd integer, will set if not
        this function pads the data so that the edges are equal to the
        orginal value
    """
    if int(box_size) % 2 == 0:  # make sure box_size is odd integer
        box_size = int(box_size) + 1  # if even, add one
    else:
        box_size = int(box_size)  # if not even (e.g., float), make integer

    box = np.ones(box_size) / box_size  # convolution kernal for moving window
    y_pad = np.pad(y, (box_size // 2, box_size - 1 - box_size // 2), mode='edge')  # padd for edge effects
    y_smooth = np.convolve(y_pad, box, mode='valid')  # convolve, 'valid' key work trims pad
    return y_smooth


def extract_well_data(name, well_df, end_date, min_samples):
    if len(well_df) >= min_samples:
        # if (well_df['date'].min() < start_date) and (well_df['date'].max() > end_date):
        # elevation = well_df['gse'].unique()[0]
        df = pd.DataFrame(index=well_df['date'].values, data=well_df['ts_value'].values, columns=[name])
        df = df[np.logical_not(df.index.duplicated())]
        return df


def interp_well(wells_df, gap_size, pad, spacing):
    well_interp_df = pd.DataFrame()
    # create a time index to interpolate over - cover entire range
    interp_index: pd.DatetimeIndex = pd.date_range(start=min(wells_df.index),
                                                   freq=spacing,
                                                   end=max(wells_df.index))
    # loop over each well, interpolate data using pchip
    for well in wells_df:
        temp_df = wells_df[well].dropna()  # available data for a well

        x_index = temp_df.index.astype('int')  # dates for available data

        x_diff = temp_df.index.to_series().diff()  # data gap sizes

        fit2 = interpolate.pchip(x_index, temp_df)  # pchip fit to data

        ynew = fit2(interp_index.astype('int'))  # interpolated data on full range

        interp_df = pd.DataFrame(ynew, index=interp_index, columns=[well])

        # replace data in gaps of > 1 year with nans

        gaps = np.where(x_diff > gap_size)  # list of indexes where gaps are large

        for g in gaps[0]:
            start = x_diff.index[g - 1] + datetime.timedelta(days=pad)

            end = x_diff.index[g] - datetime.timedelta(days=pad)

            interp_df[start:end] = np.nan

        beg_meas_date = x_diff.index[0]  # date of 1st measured point

        end_meas_date = temp_df.index[-1]  # date of last measured point

        mask1 = (interp_df.index < beg_meas_date)  # locations of data before 1st measured point

        interp_df[mask1] = np.nan  # blank out data before 1st measured point

        mask2 = (interp_df.index >= end_meas_date)  # locations of data after the last measured point

        interp_df[mask2] = np.nan  # blank data from last measured point

        # add the interp_df data to the full data frame

        well_interp_df = pd.concat([well_interp_df, interp_df], join="outer", axis=1, sort=False)
    return well_interp_df


def get_time_bounds(url):
    # This function returns the first and last available time
    # from a url of a getcapabilities page located on a Thredds Server
    f = urllib.request.urlopen(url)
    tree = ET.parse(f)
    root = tree.getroot()
    # These lines of code find the time dimension information for the netcdf on the Thredds server
    dim = root.findall('.//{http://www.opengis.net/wms}Dimension')
    dim = dim[0].text
    times = dim.split(',')
    times.pop(0)
    timemin = times[0]
    timemax = times[-1]
    # timemin and timemax are the first and last available times on the specified url
    return timemin, timemax


def get_thredds_value(server, layer, bbox):
    # This function returns a pandas dataframe of the timeseries values of a specific layer
    # at a specific latitude and longitude from a file on a Thredds server
    # server: the url of the netcdf desired netcdf file on the Thredds server to read
    # layer: the name of the layer to extract timeseries information from for the netcdf file
    # lat: the latitude of the point at which to extract the timeseries
    # lon: the longitude of the point at which to extract the timeseries
    # returns df: a pandas dataframe of the timeseries at lat and lon for the layer in the server netcdf file
    # calls the getTimeBounds function to get the first and last available times for the netcdf file on the server
    time_min, time_max = get_time_bounds(server + "?service=WMS&version=1.3.0&request=GetCapabilities")
    # These lines properly format a url request for the timeseries of a speific layer from a netcdf on
    # a Thredds server
    server = f'{server}?service=WMS&version=1.3.0&request=GetFeatureInfo&CRS=CRS:84&QUERY_LAYERS={layer}'
    server = f'{server}&X=0&Y=0&I=0&J=0&BBOX={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}'
    server = f'{server}&WIDTH=1&Height=1&INFO_FORMAT=text/xml'
    server = f'{server}&TIME={time_min}/{time_max}'
    f = request.urlopen(server)
    tree = ET.parse(f)
    root = tree.getroot()
    features = root.findall('FeatureInfo')
    times = []
    values = []
    for child in features:
        time = datetime.datetime.strptime(child[0].text, "%Y-%m-%dT%H:%M:%S.%fZ")
        times.append(time)
        values.append(child[1].text)

    df = pd.DataFrame(index=times, columns=[layer], data=values)
    df[layer] = df[layer].replace('none', np.nan).astype(float)
    return df


def sat_resample(gldas_df):
    # resamples the data from both datasets to a monthly value,
    # uses the mean of all measurements in a month
    # first resample to daily values, then take the start of the month
    gldas_df = gldas_df.resample('D').mean()
    # D is daily, mean averages any values in a given day, if no data in that day, gives NaN

    gldas_df.interpolate(method='pchip', inplace=True, limit_area='inside')

    gldas_df = gldas_df.resample('MS').first()
    # MS means "month start" or to the start of the month, this is the interpolated value

    # gldas_df.to_hdf('data.h5', key='gldas_df', mode='a')  # append data to the file
    # print(gldas_df.describe())
    return gldas_df


def sat_rolling_window(years, gldas_df):
    names = list(gldas_df.columns)
    new_names = copy.deepcopy(names)  # names is a list of the varibiles in the data frame, need to unlink for loop
    # This loop adds the yearly, 3-year, 5-year, and 10-year rolling averages of each variable to the dataframe
    # rolling averages uses the preceding time to compute the last value,
    # e.g., using the preceding 5 years of data to get todays
    for name in names:
        for year in years:
            new = name + '_yr' + str(year).zfill(2)
            gldas_df[new] = gldas_df[name].rolling(year * 12).mean()
            new_names.append(new)
    return gldas_df, new_names


def norm_training_data(in_df, ref_df):
    norm_in_df = (in_df - ref_df.min().values) / (
            ref_df.max().values - ref_df.min().values)  # use values as df sometimes goofs
    return norm_in_df


def input_to_hidden(x, Win, b):
    # setup matrixes
    a = np.dot(x, Win) + b
    a = np.maximum(a, 0, a)  # relu
    return a


def predict(in_values, W_in, b, W_out):
    x = input_to_hidden(in_values, W_in, b)
    y = np.dot(x, W_out)
    return y


def impute_data(comb_df, well_names, names):
    # for out test set we will impute everything
    imputed_df = pd.DataFrame(index=comb_df.index)
    for well in well_names:  # list of the wells in the aquifer
        train_nona_df = comb_df.dropna(subset=[well])  # drop any rows with na in well (measured) data
        labels_df = train_nona_df[well]  # measured data used as "labels" or truth in training
        tx_df = train_nona_df[names]  # data we will predict with only over the test period
        all_tx_df = comb_df[names]  # data over the full period, will use for imputation

        tx = tx_df.values  # convert to an array
        x1 = np.column_stack(np.ones(tx.shape[0])).T  # bias vector of 1's
        tx = np.hstack((tx, x1))  # training matrix
        ty = labels_df.values
        input_length = tx.shape[1]
        hidden_units = 500
        lamb_value = 100
        W_in = np.random.normal(size=[input_length, hidden_units])
        b = np.random.normal(size=[hidden_units])
        print('Well Number ', well)

        # now do the matrix multiplication
        X = input_to_hidden(tx, W_in, b)  # setup matrix for multiplication, it is a function
        I = np.identity(X.shape[1])
        I[X.shape[1] - 1, X.shape[1] - 1] = 0
        I[X.shape[1] - 2, X.shape[1] - 2] = 0
        W_out = np.linalg.lstsq(X.T.dot(X) + lamb_value * I, X.T.dot(ty), rcond=-1)[0]
        all_tx_values = all_tx_df.values
        a1 = np.column_stack(np.ones(all_tx_values.shape[0])).T
        all_tx_values = np.hstack((all_tx_values, a1))
        predict_values = predict(all_tx_values, W_in, b, W_out)  # it is a function
        pre_name = f'{well}_imputed'
        imputed_df[pre_name] = pd.Series(predict_values, index=imputed_df.index)

    return imputed_df


def renorm_data(in_df, ref_df):
    assert in_df.shape[1] == ref_df.shape[1], 'must have same # of columns'
    renorm_df = (in_df * (ref_df.max().values - ref_df.min().values)) + ref_df.min().values
    return renorm_df


def plot_imputed_results(wells_df, combined_df, imputed_df, well_names):
    im_plots = plt_pdf.PdfPages('Imputed_well_plots.pdf')
    for well in well_names:
        i_name = f'{well}_imputed'
        plt.plot(combined_df[well], '*', label='Combined')
        plt.plot(wells_df[well], '.', label='Measured', linewidth=0.5)

        plt.plot(imputed_df[i_name], 'b-', label='Imputed Data', linewidth=0.5)

        plt.title(well)
        plt.legend()
        im_plots.savefig()
        # plt.show()
        plt.close('all')
    im_plots.close()


def create_grid_coords(x_c, y_c, x_steps):
    # create grid coordinates fro kriging, make x and y steps the same
    # x_steps is the number of cells in the x-direction
    n_bin = np.absolute((max(x_c) - min(x_c)) / x_steps)  # determine step size (positive)
    # make grid 10 bin steps bigger than date, will give 110 steps in x-direction
    grid_x = np.arange(min(x_c) - 5 * n_bin, max(x_c) + 5 * n_bin, n_bin)  # make grid 10 steps bigger than data
    grid_y = np.arange(min(y_c) - 5 * n_bin, max(y_c) + 5 * n_bin, n_bin)  # make grid 10 steps bigger than data

    return grid_x, grid_y


def krig_field_generate(var_fitted, x_c, y_c, values, grid_x, grid_y):
    # use GSTools to krig  the well data, need coords and value for each well
    # use model variogram paramters generated by GSTools
    # fast - is faster the variogram fitting
    krig_map = gs.krige.Ordinary(var_fitted, cond_pos=[x_c, y_c], cond_val=values)
    krig_map.structured([grid_x, grid_y])  # krig_map.field is the numpy array of values
    return krig_map


def rbf_field_generate(x_c, y_c, values, grid_x, grid_y):
    # use sci.py rbf interpolation function
    # poorly implemented - many StackOverflow comments say don't use. U-Mich has a good implementation
    # don't want as you get severe over/under shoot outside convex hull - and some inside
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    rbfi = sci_intrp.Rbf(x_c, y_c, values, epsilon=2, function='quintic', extrapolate=False)
    # functions - thin_plate, multiquadric, inverse, gaussian, linear, cubic, quintic
    rbf_map = rbfi(mesh_x, mesh_y)
    return rbf_map, mesh_x, mesh_y


def griddata_field_generate(x_c, y_c, values, grid_x, grid_y):
    # use sci.py griddata interpolation function
    # reasonable, only has nearest (step function), linear, and cubic methods
    # does not extrapolate outside convex hull
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    rbf_map = sci_intrp.griddata((x_c, y_c), values, (mesh_x, mesh_y), method='cubic')
    # functions - thin_plate, multiquadric, inverse, gaussian, linear, cubic, quintic
    return rbf_map, mesh_x, mesh_y


def plot_krig_data(krig_map, measurement, krig_plots, x_c, y_c, values):
    # ---------- Plot a map for review -------------
    # could extract field and use plot_np_data
    # krig_array = krig_map.field
    krig_map.plot()  # plot the kriged results
    plt.plot(x_c, y_c, "k.")  # plot the well locations on the same plot
    for x, y, z in zip(x_c, y_c, values):  # label each well with gw surface elevation
        label = '{:.2f}'.format(z)
        plt.annotate(label, (x, y), ha='center')
    plt.title(measurement)
    krig_plots.savefig()
    plt.close('all')


def plot_np_data(nn_map, mesh_x, mesh_y, measurement, nn_plots, title, x_c, y_c, values):
    # --------plot nn maps for review --------
    # plots a numpy array
    fig, ax = plt.subplots()
    cs = plt.contourf(mesh_x, mesh_y, nn_map)
    plt.clabel(cs, inline=0)
    plt.plot(x_c, y_c, "k.")  # plot the well locations on the same plot
    for x, y, z in zip(x_c, y_c, values):  # label each well with gw surface elevation
        label = '{:.2f}'.format(z)
        plt.annotate(label, (x, y), ha='center')
    ax.set_title(measurement)
    ax.set_xlabel(title)
    nn_plots.savefig()
    plt.close('all')


def krig_map_generate(var_fitted, x_c, y_c, values, grid_x, grid_y):
    # use GSTools to krig  the well data, need coords and value for each well
    # use model variogram paramters generated by GSTools
    krig_map = gs.krige.Ordinary(var_fitted, cond_pos=[x_c, y_c], cond_val=values)
    krig_map.structured([grid_x, grid_y])
    return krig_map


def fit_model_var(coords_df, x_c, y_c, values):
    # fit the model varigrom to the experimental variogram
    bin_num = 40  # number of bins in the experimental variogram

    # first get the coords and determine distances
    x_delta = max(x_c) - min(x_c)  # distance across x coords
    y_delta = max(y_c) - min(y_c)  # distance across y coords
    max_dist = np.sqrt(np.square(x_delta + y_delta)) / 4  # assume correlated over 1/4 of distance

    # setup bins for the variogram
    bins_c = np.linspace(0, max_dist, bin_num)  # bin edges in variogram, bin_num of bins

    # compute the experimental variogram
    bin_cent_c, gamma_c = gs.vario_estimate_unstructured((x_c, y_c), values, bins_c)
    # bin_center_c is the "lag" of the bin, gamma_c is the value

    gamma_c = smooth(gamma_c, 5)  # smooth the experimental variogram to help fitting - moving window with 5 samples

    # fit the model variogram
    # potential models are: Gaussian, Exponential, Matern, Rational, Stable, Linear,
    #                       Circular, Spherical, and Intersection
    fit_var = gs.Stable(dim=2)
    fit_var.fit_variogram(bin_cent_c, gamma_c, nugget=False, estimator='cressie')  # fit the model variogram

    # print('max distance', max_dist,'var len scale', fit_var.len_scale)
    # check to see of range of varigram is very small (problem with fit), it so, set it to a value
    # also check to see if it is too long and set it to a value
    if fit_var.len_scale < max_dist / 3:  # check if too short
        fit_var.len_scale = max_dist / 3  # set to value
        # print('too short, set len_scale to: ', max_dist/3)
    elif fit_var.len_scale > max_dist * 1.5:  # check if too long
        fit_var.len_scale = max_dist  # set to value
        # print('too long, set len_scale to: ', max_dist)

    plt_var = False
    if plt_var:
        # plot the variogram to show fit and print out variogram paramters
        # should make it save to pdf file
        ax1 = fit_var.plot(x_max=max_dist)  # plot model variogram
        ax1.plot(bin_cent_c, gamma_c)  # plot experimental variogram
        # krig_plots.savefig()
        plt.close('all')
    return fit_var


def extract_query_objects(region_id, aquifer_id, variable):
    session = get_session_obj()
    aquifer_obj = session.query(gf2.ST_AsText(Aquifer.geometry), Aquifer.aquifer_name).filter(
        Aquifer.region_id == region_id,
        Aquifer.id == aquifer_id).first()
    bbox = wkt.loads(aquifer_obj[0]).bounds
    print(bbox)
    wells_query = session.query(Well).filter(Well.aquifer_id == aquifer_id)
    wells_query_df = pd.read_sql(wells_query.statement, session.bind)
    well_ids = [int(well_id) for well_id in wells_query_df.id.values]
    # well_dict = {well.id: well.gse for well in wells_query_df.itertuples()}
    m_query = session.query(Measurement).filter(Measurement.well_id.in_(well_ids),
                                                Measurement.variable_id == variable)
    measurements_df = pd.read_sql(m_query.statement, session.bind)
    # measurements_df['gse'] = measurements_df['well_id'].map(well_dict)
    measurements_df['date'] = pd.to_datetime(measurements_df.ts_time, infer_datetime_format=True)

    session.close()

    return (bbox,
            wells_query_df,
            measurements_df,
            aquifer_obj)


def krig_imputed_wells(years_df, coords_df, values, x_coords, y_coords, grid_x, grid_y):
    krig_plots = plt_pdf.PdfPages('Krig.pdf')
    for measurement in years_df:
        # loop through the data
        values = years_df[measurement].values
        # fit the model variogram to the experimental variogram
        var_fitted = fit_model_var(coords_df, x_coords, y_coords, values)

        krig_map = krig_map_generate(var_fitted, x_coords, y_coords, values, grid_x, grid_y)
        # krig_map.field provides the 2D array of values

        # ---------- Plot a map for review -------------
        krig_map.plot()  # plot the kriged results
        # plt.plot(x_coords, y_coords, "k.")  # plot the well locations on the same plot
        # for x, y, z in zip(x_coords, y_coords, values):  # label each well with gw surface elevation
        #     label = '{:.2f}'.format(z)
        #     plt.annotate(label, (x, y), ha='center')
        plt.title(measurement)
        krig_plots.savefig()
        plt.close('all')
    krig_plots.close()


def generate_nc_file(file_name, grid_x, grid_y, years_df, coords_df, x_coords, y_coords):
    print('generating netcdf file')
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file_name)
    h = netCDF4.Dataset(file_path, 'w', format="NETCDF4")
    lat_len = len(grid_y)
    lon_len = len(grid_x)
    time = h.createDimension("time", 0)
    lat = h.createDimension("lat", lat_len)
    lon = h.createDimension("lon", lon_len)
    latitude = h.createVariable("lat", np.float64, ("lat"))
    longitude = h.createVariable("lon", np.float64, ("lon"))
    time = h.createVariable("time", np.float64, ("time"), fill_value="NaN")
    ts_value = h.createVariable("tsvalue", np.float64, ('time', 'lon', 'lat'), fill_value=-9999)
    latitude.long_name = "Latitude"
    latitude.units = "degrees_north"
    latitude.axis = "Y"
    longitude.long_name = "Longitude"
    longitude.units = "degrees_east"
    longitude.axis = "X"
    time.axis = "T"
    time.units = 'days since 0001-01-01 00:00:00 UTC'

    latitude[:] = grid_y[:]
    longitude[:] = grid_x[:]

    time_counter = 0
    for measurement in years_df:
        # loop through the data
        values = years_df[measurement].values

        beg_time = timer()  # time the kriging method including variogram fitting
        # fit the model variogram to the experimental variogram
        var_fitted = fit_model_var(coords_df, x_coords, y_coords, values)  # fit variogram
        krig_map = krig_field_generate(var_fitted, x_coords, y_coords, values, grid_x, grid_y)  # krig data
        # krig_map.field provides the 2D array of values
        end_time = timer()
        print('krig time = ', end_time - beg_time)
        time[time_counter] = measurement.toordinal()
        ts_value[time_counter, :, :] = krig_map.field
        time_counter += 1

    h.close()
    print(file_path)
    return Path(file_path)


def clip_nc_file(file_path, aquifer_obj, region_id):
    thredds_directory = app.get_custom_setting('gw_thredds_directoy')
    aquifer_name = aquifer_obj[1].replace(" ", "_")
    aquifer_dir = os.path.join(thredds_directory, str(region_id), str(aquifer_name))
    if not os.path.exists(aquifer_dir):
        os.makedirs(aquifer_dir)

    output_file = os.path.join(aquifer_dir, file_path.name)
    temp_dir = file_path.parent.absolute()
    interp_nc = xarray.open_dataset(file_path)
    interp_nc.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    interp_nc.rio.write_crs("epsg:4326", inplace=True)

    aquifer_geom = wkt.loads(aquifer_obj[0])
    aquifer_gdf = gpd.GeoDataFrame({'name': ['random'], 'geometry': [aquifer_geom]})
    # aq_geom_str = json.dumps(mapping(aquifer_geom[0]))
    # print(type(aq_geom_str))
    # cropping_geometries = [geojson.loads(aq_geom_str)]
    clipped_nc = interp_nc.rio.clip(aquifer_gdf.geometry.apply(mapping), crs=4326, drop=True)
    clipped_nc.to_netcdf(output_file)
    shutil.rmtree(temp_dir)

    return output_file


def mlr_interpolation(mlr_dict):
    region_id = mlr_dict['region']
    aquifer_id = mlr_dict['aquifer']
    variable = mlr_dict['variable']
    min_samples = mlr_dict['min_samples']
    gap_size = mlr_dict['gap_size']
    pad = mlr_dict['pad']
    spacing = mlr_dict['spacing']

    start_date = datetime.datetime(mlr_dict['start_date'], 1, 1)
    end_date = datetime.datetime(mlr_dict['end_date'], 1, 1)

    bbox, wells_query_df, measurements_df, aquifer_obj = extract_query_objects(region_id, aquifer_id, variable)
    pdsi_df = get_thredds_value(SERVER1, LAYER1, bbox)  # pdsi values
    soilw_df = get_thredds_value(SERVER2, LAYER2, bbox)  # soilw values
    gldas_df = pd.concat([pdsi_df, soilw_df], join="outer", axis=1)
    gldas_df = sat_resample(gldas_df)
    gldas_df, names = sat_rolling_window(YEARS, gldas_df)
    print('gldas', gldas_df)

    wells_df = pd.concat([extract_well_data(name, group, end_date, min_samples)
                          for name, group in measurements_df.groupby('well_id')], axis=1, sort=False)
    print('wells_df', wells_df)
    wells_df.drop_duplicates(inplace=True)
    well_names = wells_df.columns
    # wells_df.to_csv('wells_df.csv')
    well_interp_df = interp_well(wells_df, gap_size, pad, spacing)
    print('well_interp_df', well_interp_df)
    # well_interp_df.to_csv('well_interp.csv')
    # combine the  data from the wells and the satellite observations  to a single dataframe (combined_df)
    # this will have a row for every measurement (on the start of the month) a column for each well,
    # and a column for pdsi and soilw and their rolling averages, and potentially offsets
    combined_df = pd.concat([well_interp_df, gldas_df], join="outer", axis=1, sort=False)
    combined_df.dropna(subset=names, inplace=True)  # drop rows where there are no satellite data
    print('combined_df', combined_df)
    norm_df = norm_training_data(combined_df, combined_df)
    print('norm_df', norm_df)
    imputed_norm_df = impute_data(norm_df, well_names, names)
    ref_df = combined_df[well_names]
    imputed_df = renorm_data(imputed_norm_df, ref_df)
    # print(imputed_df)

    # plot_imputed_results(wells_df, combined_df, imputed_df, well_names)
    imputed_well_names = imputed_df.columns  # create a list of well names
    loc_well_names = [int(strg.replace('_imputed', '')) for strg in imputed_well_names]  # strip off "_imputed"
    coords_df = wells_query_df[wells_query_df.id.isin(loc_well_names)]
    x_coords = coords_df.longitude.values
    y_coords = coords_df.latitude.values

    # create grid
    x_steps = 400  # steps in x-direction, number of y-steps will be computed with same spacing, adds 10%
    grid_x, grid_y = create_grid_coords(x_coords, y_coords, x_steps)  # coordinates for x and y axis - not full grid

    skip_month = 48  # take data every nth month (skip_months), e.g., 60 = every 5 years
    years_df = imputed_df.iloc[::skip_month].T  # extract every nth month of data and transpose array
    print(len(years_df))
    aquifer_name = aquifer_obj[1].replace(" ", "_")
    file_name = f'{aquifer_name}_{variable}_{time.time()}.nc'
    # setup a netcdf file to store the time series of rasters
    #
    nc_file_path = generate_nc_file(file_name, grid_x, grid_y, years_df, coords_df, x_coords, y_coords)
    final_nc_path = clip_nc_file(nc_file_path, aquifer_obj, region_id)
    return final_nc_path


def process_interpolation(info_dict):
    print(info_dict)
    from_wizard = info_dict['from_wizard']
    if from_wizard == 'true':
        pass
    else:
        pass

    start_date = int(info_dict['start_date'])
    end_date = int(info_dict['end_date'])
    interval = int(info_dict['frequency'])
    iterations = (end_date - start_date) / (interval + 1)
    start_time = calendar.timegm(datetime.datetime(start_date, 1, 1).timetuple())
    end_time = calendar.timegm(datetime.datetime(end_date, 1, 1).timetuple())

    time_u = "Y"

    if interval <= .5:
        time_u = "M"
        time_v = 6
        iterations += 1
        if interval == .25:
            iterations += 2
            time_v = 3
    else:
        time_v = int(interval)

    resample_rate = f'{time_v}{time_u}'

    temporal_interpolation = info_dict['temporal_interpolation']
    min_samples = int(info_dict['min_samples'])

    region_id = int(info_dict['region'])
    aquifer_id = info_dict['aquifer']
    if aquifer_id == 'all':
        aquifer_list = [aquifer[1] for aquifer in get_region_aquifers_list(region_id)]
    else:
        aquifer_list = [int(aquifer_id)]

    variable = int(info_dict['variable'])
    min_ratio = float(info_dict['min_ratio'])
    time_tolerance = int(info_dict['time_tolerance'])
    gap_size = info_dict['gap_size']
    pad = int(info_dict['pad'])
    spacing = info_dict['spacing']

    if temporal_interpolation == 'MLR':
        for aquifer in aquifer_list:
            mlr_dict = {'region': region_id,
                        'aquifer': aquifer,
                        'min_samples': min_samples,
                        'variable': variable,
                        'start_time': start_time,
                        'end_time': end_time,
                        'min_ratio': min_ratio,
                        'time_tolerance': time_tolerance,
                        'start_date': start_date,
                        'end_date': end_date,
                        'resample_rate': resample_rate,
                        'gap_size': gap_size,
                        'pad': pad,
                        'spacing': spacing}
            mlr_interpolation(mlr_dict)

    end_time = time.time()
    total_time = end_time - start_time
    return total_time

# process_interpolation(INFO_DICT)
