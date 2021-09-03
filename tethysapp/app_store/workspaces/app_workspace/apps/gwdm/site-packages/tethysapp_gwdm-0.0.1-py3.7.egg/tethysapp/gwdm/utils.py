import calendar
import json
import os
import glob
import shutil
import time
import uuid
from datetime import datetime
from typing import List, Any, Dict, Tuple, Union

import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import simplejson
import xarray as xr
from pandarallel import pandarallel
from shapely import wkt
from sqlalchemy.sql import func
from tethys_sdk.gizmos import (TextInput,
                               SelectInput)
from thredds_crawler.crawl import Crawl

from .app import Gwdm as app
from .model import (Region,
                    Aquifer,
                    Well,
                    Measurement,
                    Variable)


def user_permission_test(user):
    """
    Check the permissions of the user

    Args:
        user: Django User

    Returns:
        bool of if user is superuser or staff
    """
    return user.is_superuser or user.is_staff


def get_session_obj():
    """
    Helper function to get SQL Alchemy Persistent Store Session Object

    Returns:
        SQL Alchemy Session Object
    """
    app_session = app.get_persistent_store_database('gwdb', as_sessionmaker=True)
    session = app_session()
    return session


def get_regions() -> List:
    """
    Get All Existing Regions from the Database

    Returns:
        list of tuples with region name and region id
    """
    session = get_session_obj()
    regions = session.query(Region).all()
    region_list = [(region.region_name, region.id) for region in regions]
    session.close()
    return region_list


def get_region_name(region_id: int) -> str:
    """
    Get Region Name for a given region id

    Returns:
        Region name string
    """
    session = get_session_obj()
    region_name = session.query(Region.region_name).filter(Region.id == region_id).first()[0]
    session.close()
    return region_name


def get_region_select():
    """
    Generate Region Select Gizmo

    Returns:
        Tethys Select Input Gizmo Object to select regions
    """
    region_list = get_regions()
    region_select = SelectInput(display_text='Select a Region',
                                name='region-select',
                                options=region_list,)

    return region_select


def get_aquifer_select(region_id: Union[int, None], aquifer_id: bool = False) -> Any:
    """
    Generate Aquifer Select Gizmo

    Args:
        region_id: Region Id as listed in the Region table
        aquifer_id: Boolean to decide the aquifer id type

    Returns:
        Aquifer Select Gizmo Object. Used to generate an aquifer select dropdown.
    """
    aquifer_list = []
    if region_id is not None:
        session = get_session_obj()
        aquifers = session.query(Aquifer).filter(Aquifer.region_id == region_id)

        for aquifer in aquifers:
            if aquifer_id:
                aquifer_list.append(("%s" % aquifer.aquifer_name, aquifer.id))
            else:
                aquifer_list.append(("%s" % aquifer.aquifer_name, aquifer.aquifer_id))
        session.close()

    aquifer_select = SelectInput(display_text='Select an Aquifer',
                                 name='aquifer-select',
                                 options=aquifer_list,)

    return aquifer_select


def get_variable_list() -> List:
    """
    Generate list of all variables in the database

    Returns:
        a list of tuples with variable name, units and id
    """
    session = get_session_obj()
    variables = session.query(Variable).all()
    variable_list = [(f'{variable.name}, {variable.units}', variable.id) for variable in variables]
    session.close()
    return variable_list


def get_variable_select() -> Any:
    """
    Generate Variable Select Gizmo

    Returns:
        Tethys Select Input Gizmo Object to select variables
    """
    variable_list = get_variable_list()

    variable_select = SelectInput(display_text='Select Variable',
                                  name='variable-select',
                                  options=variable_list,)
    return variable_select


def get_region_variables_list(region_id: Union[int, None]) -> List:
    """
    Get a list of variables within a given region

    Args:
        region_id: Region Id as listed in the Region table

    Returns:
        a list of tuples with variable name, units and id within a given region
    """

    if region_id is not None:
        session = get_session_obj()
        variables = (session.query(Variable)
                     .join(Measurement, Measurement.variable_id == Variable.id)
                     .join(Well, Measurement.well_id == Well.id)
                     .join(Aquifer, Well.aquifer_id == Aquifer.id)
                     .filter(Aquifer.region_id == region_id)
                     .distinct()
                     )
        variable_list = [(f'{variable.name}, {variable.units}', variable.id) for variable in variables]
        if len(variable_list) == 0:
            variable_list = get_variable_list()
        session.close()
    else:
        variable_list = get_variable_list()
    return variable_list


def get_metrics() -> Any:
    """
    Generate Summary Statistics of the database

    Returns:
        Plotly Figure Object of a Pandas DataFrame grouped by Region, Variable, and Measurements
    """
    session = get_session_obj()
    metrics_query = (session.query(Region.region_name, Variable.name.label('variable_name'),
                                   func.count(Measurement.id).label('measurements'))
                     .join(Measurement, Measurement.variable_id == Variable.id)
                     .join(Well, Measurement.well_id == Well.id)
                     .join(Aquifer, Well.aquifer_id == Aquifer.id)
                     .join(Region, Region.id == Aquifer.region_id)
                     .group_by(Region.region_name, Variable.name)
                     )
    metrics_df = pd.read_sql(metrics_query.statement, session.bind)
    session.close()

    fig = go.Figure(data=[go.Table(
        header=dict(values=['Region Name', 'Variable Name', 'Number of Measurements'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[metrics_df.region_name, metrics_df.variable_name, metrics_df.measurements],
                   fill_color='lavender',
                   align='left'))
    ])

    return fig


def get_region_aquifers_list(region_id: int) -> List:
    """
    Generate a list of aquifers for a given region

    Args:
        region_id: Region Id as listed in the Region table

    Returns:
        A list of aquifers tuples with aquifer name and if for a given region
    """
    session = get_session_obj()
    aquifers = session.query(Aquifer).filter(Aquifer.region_id == region_id)
    aquifers_list = [[aquifer.aquifer_name, aquifer.id] for aquifer in aquifers]
    session.close()
    return aquifers_list


def get_aquifers_list() -> List:
    """
    Generate a list of all the aquifers in the database

    Returns:
        A list of all aquifers tuples with aquifer name and id
    """
    session = get_session_obj()
    aquifers = session.query(Aquifer).all()
    aquifers_list = [[aquifer.aquifer_name, aquifer.id] for aquifer in aquifers]
    session.close()
    return aquifers_list


def get_num_wells() -> int:
    """
    Get a count of unique wells in the database

    Returns:
        The number of unique wells in the database
    """
    session = get_session_obj()
    wells = session.query(Well.id).distinct().count()
    session.close()
    return wells


def get_num_measurements() -> int:
    """
    Get a count of all the measurements in the database

    Returns:
        The total number of measurements in the database
    """
    session = get_session_obj()
    measurements = session.query(Measurement.id).distinct().count()
    session.close()
    return measurements


def get_region_variable_select(region_id: Union[int, None]) -> Any:
    """
    Generate a Variable Select Tethys Gizmo

    Args:
        region_id: Region Id as listed in the database

    Returns:
        A Variable Select Input Tethys Gizmo Object
    """
    variable_list = get_region_variables_list(region_id)
    variable_select = SelectInput(display_text='Select Variable',
                                  name='variable-select',
                                  options=variable_list,
                                  attributes={'id': 'variable-select'},
                                  classes='variable-select')

    return variable_select


def process_region_shapefile(shapefile: Any,
                             region_name: str,
                             app_workspace: Any) -> Dict:
    """
    Process Uploaded Region Shapefile

    Args:
        shapefile: list of shapefile files
        region_name: Region Name
        app_workspace: Temporary App workspace path

    Returns:
        Response dict with success or error string
    """

    session = get_session_obj()
    temp_dir = None
    try:
        gdf, temp_dir = get_shapefile_gdf(shapefile, app_workspace)
        gdf['region_name'] = region_name
        gdf = gdf.dissolve(by='region_name')
        region = Region(region_name=region_name, geometry=gdf.geometry.values[0])
        session.add(region)
        session.commit()
        session.close()

        return {"success": "success"}

    except Exception as e:
        session.close()
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}
    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def process_aquifer_shapefile(shapefile: Any,
                              region_id: int,
                              name_attr: str,
                              id_attr: str,
                              app_workspace: Any) -> Dict:
    """
    Process uploaded auifer shapefile

    Args:
        shapefile: List of shapefile files
        region_id: Region id as listed in the database
        name_attr: Aquifer Name Column
        id_attr: Aquifer Id Column
        app_workspace: Temp App workspace

    Returns:
        Response dict with success or error string
    """
    session = get_session_obj()
    temp_dir = None

    def add_aquifer_apply(row):
        aquifer = Aquifer(region_id=region_id,
                          aquifer_name=row.aquifer_name,
                          aquifer_id=row.aquifer_id,
                          geometry=row.geometry)
        return aquifer
    try:
        start_time = time.time()
        pandarallel.initialize()
        gdf, temp_dir = get_shapefile_gdf(shapefile, app_workspace)
        gdf = gdf.dissolve(by=name_attr, as_index=False)
        # gdf.to_csv('texas_aquifers.csv')
        rename_cols = {name_attr: 'aquifer_name',
                       id_attr: 'aquifer_id'}
        gdf.rename(columns=rename_cols, inplace=True)
        gdf = gdf[['aquifer_name', 'aquifer_id', 'geometry']]
        aquifer_list = gdf.parallel_apply(add_aquifer_apply, axis=1)

        session.add_all(aquifer_list)
        session.commit()
        session.close()
        end_time = time.time()
        total_time = (end_time - start_time)

        return {"success": "success", "total_time": total_time}

    except Exception as e:
        session.close()
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}
    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def get_shapefile_gdf(shapefile: Any,
                      app_workspace: Any,
                      polygons: bool = True) -> Tuple[Any, Any]:
    """
    Helper function to process uploaded shapefile

    Args:
        shapefile: List of shapefile files
        app_workspace: Temp App Workspace
        polygons: Boolean to determine a polygon or point shapefile

    Returns:
        GeoDataFrame of the shapefile, Temp Directory of the processed shapefile
    """
    temp_id = uuid.uuid4()
    temp_dir = os.path.join(app_workspace.path, str(temp_id))
    os.makedirs(temp_dir)
    gbyos_pol_shp = None
    upload_csv = None
    gdf = None

    for f in shapefile:
        f_name = f.name
        f_path = os.path.join(temp_dir, f_name)

        with open(f_path, 'wb') as f_local:
            f_local.write(f.read())

    for file in os.listdir(temp_dir):
        # Reading the shapefile only
        if file.endswith(".shp") or file.endswith(".geojson") or file.endswith(".json"):
            f_path = os.path.join(temp_dir, file)
            gbyos_pol_shp = f_path

        if file.endswith(".csv"):
            f_path = os.path.join(temp_dir, file)
            upload_csv = f_path

    if gbyos_pol_shp is not None:
        gdf = gpd.read_file(gbyos_pol_shp)

    if upload_csv is not None:
        df = pd.read_csv(upload_csv, engine='python')
        if polygons:
            gdf = gpd.GeoDataFrame(df, crs={'init': 'epsg:4326'}, geometry=df['geometry'].apply(wkt.loads))
        else:
            gdf = df

    return gdf, temp_dir


def get_shapefile_attributes(shapefile: Any,
                             app_workspace: Any,
                             polygons: bool = True) -> Any:
    """
    Get attributes from the uploaded shapefile

    Args:
        shapefile: list of shapefiles
        app_workspace: Temporary App workspace
        polygons: Boolean to indicate if the shapefile is polygon or point geometries

    Returns:
        list of attributes in the shapefile. returns an error string on fail.
    """
    temp_dir = None
    try:

        gdf, temp_dir = get_shapefile_gdf(shapefile, app_workspace, polygons)

        attributes = gdf.columns.values.tolist()

        return attributes

    except Exception as e:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}
    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def geoserver_text_gizmo() -> Any:
    """
    Geoserver Gizmo Input to Store Geoserver WFS Endpoint

    Returns:
        A Hidden Tethys Gizmo Input with Geoserver WFS Endpoint
    """
    geoserver_wfs_endpoint = app.get_spatial_dataset_service('primary_geoserver', as_wfs=True)

    geoserver_text_input = TextInput(display_text='Geoserver',
                                     name='geoserver-text-input',
                                     placeholder=geoserver_wfs_endpoint,
                                     attributes={'value': geoserver_wfs_endpoint},
                                     classes="hidden")

    return geoserver_text_input


def thredds_text_gizmo() -> Any:
    """
    Thredds Gizmo Input to Store Thredds WMS Endpoint

    Returns:
        A Hidden Tethys Gizmo Input with Thredds WMS Endpoint
    """
    thredds_endpoint = app.get_spatial_dataset_service('primary_thredds', as_endpoint=True)
    thredds_text_input = TextInput(display_text='Thredds',
                                   name='thredds-text-input',
                                   placeholder=thredds_endpoint,
                                   attributes={'value': thredds_endpoint},
                                   classes="hidden")

    return thredds_text_input


def process_wells_file(lat: str,
                       lon: str,
                       well_id: str,
                       name: str,
                       gse: str,
                       attrs: str,
                       file: Any,
                       aquifer_id: str,
                       aquifer_col: str,
                       app_workspace: Any,
                       region_id: int) -> Dict:
    """
    Add the uploaded Wells File to the Database

    Args:
        lat: Latitude Column String
        lon: Longitude Column String
        well_id: Well Id Column String
        name: Name Column String
        gse: Ground Surface Elevation Column String
        attrs: Extra Attributes Column String
        file: Uploaded file object
        aquifer_id: Aquifer Id String
        aquifer_col: Aquifer Column String
        app_workspace: Temporary Workspace Directory
        region_id: Region Id as listed in the Database

    Returns:
        A response dict of success or failure
    """
    temp_dir = None
    session = get_session_obj()
    try:
        gdf, temp_dir = get_shapefile_gdf(file, app_workspace, polygons=False)

        if gdf.isnull().sum().sum() == 0:

            rename_cols = {lat: 'latitude',
                           lon: 'longitude',
                           well_id: 'well_id',
                           name: 'well_name',
                           gse: 'gse'}
            if len(aquifer_id) > 0:
                gdf['aquifer_id'] = aquifer_id
                gdf = gdf.rename(columns=rename_cols)

            if len(aquifer_col) > 0:
                rename_cols[aquifer_col] = 'aquifer_id'
                gdf.rename(columns=rename_cols, inplace=True)
                if gdf['aquifer_id'].dtypes == np.float64:
                    gdf['aquifer_id'] = gdf['aquifer_id'].astype(int)

                gdf['aquifer_id'] = gdf['aquifer_id'].astype(str)
                aquifer_ids = list(gdf['aquifer_id'].unique().astype(str))
                aquifer = (session.query(Aquifer).filter(Aquifer.region_id == region_id,
                                                         Aquifer.aquifer_id.in_(aquifer_ids)).all())
                aq_dict = {aq.aquifer_id: aq.id for aq in aquifer}
                gdf['aquifer_id'] = gdf['aquifer_id'].astype(str)
                gdf['aquifer_id'] = gdf['aquifer_id'].map(aq_dict)

            attributes = None
            if attrs:
                attributes = attrs.split(',')

            well_aquifers_list = [int(aqf_id) for aqf_id in gdf['aquifer_id'].unique()]
            wells_query = (session.query(Well.well_id).filter(Well.aquifer_id.in_(well_aquifers_list)).all())
            existing_wells = [value for value, in wells_query]
            gdf = gdf.loc[~gdf['well_id'].isin(existing_wells)]
            for row in gdf.itertuples():
                attr_dict = {}
                if attributes:
                    attr_dict = {attr: getattr(row, attr) for attr in attributes}

                attr_dict = simplejson.dumps(attr_dict, ignore_nan=True)
                attr_dict = json.loads(attr_dict)
                well = Well(aquifer_id=int(row.aquifer_id),
                            latitude=float(row.latitude),
                            longitude=float(row.longitude),
                            well_id=str(row.well_id),
                            well_name=str(row.well_name),
                            gse=float(row.gse),
                            attr_dict=attr_dict,
                            outlier=False)
                session.add(well)
            session.commit()
            session.close()

            response = {'success': 'success'}
        else:
            response = {'error': 'There were null values in the data. Please fix the data and upload again.'}
    except Exception as e:
        session.close()
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}
    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    return response


def process_measurements_file(region_id: int,
                              well_id: str,
                              m_time: str,
                              value: str,
                              time_format: str,
                              variable_id: int,
                              file: Any,
                              aquifer_id: str,
                              aquifer_col: str,
                              app_workspace: Any) -> Dict:
    """
    Add uploaded measurements to the database

    Args:
        region_id: Region Id as listed in the Database
        well_id: Well Id Column String
        m_time: Time Column String
        value: Measurement Value Column String
        time_format: Time Format String
        variable_id: Variable Id as listed in the Database
        file: Uploaded measurement file
        aquifer_id: Aquifer Id as selected by the user
        aquifer_col: Aquifer Id Column String
        app_workspace: Temporary App Workspace Directory

    Returns:
        A response dict success or failure
    """

    temp_dir = None
    session = get_session_obj()
    try:
        gdf, temp_dir = get_shapefile_gdf(file, app_workspace, polygons=False)
        rename_cols = {well_id: 'well_id',
                       m_time: 'time',
                       value: 'value'}
        gdf = gdf.rename(columns=rename_cols)
        pd.to_datetime(gdf['time'], format=time_format)
        if gdf.isnull().sum().sum() == 0:

            rename_cols = {well_id: 'well_id',
                           m_time: 'time',
                           value: 'value'}
            gdf = gdf.rename(columns=rename_cols)
            gdf['variable_id'] = variable_id

            if len(aquifer_id) > 0:
                gdf['aquifer_id'] = aquifer_id
                gdf = gdf.rename(columns=rename_cols)

            if len(aquifer_col) > 0:
                rename_cols[aquifer_col] = 'aquifer_id'
                gdf.rename(columns=rename_cols, inplace=True)
                aquifer_ids = list(gdf['aquifer_id'].unique().astype(str))
                aquifers = (session.query(Aquifer).filter(Aquifer.region_id == region_id,
                                                          Aquifer.aquifer_id.in_(aquifer_ids)).all())
                aq_dict = {aq.aquifer_id: aq.id for aq in aquifers}
                gdf['aquifer_id'] = gdf['aquifer_id'].astype(str)
                gdf['aquifer_id'] = gdf['aquifer_id'].map(aq_dict)

            aquifer_ids = list(gdf['aquifer_id'].unique().astype(str))
            well_ids = list(gdf['well_id'].unique().astype(str))
            wells = (session.query(Well).filter(Well.well_id.in_(well_ids),
                                                Well.aquifer_id.in_(aquifer_ids)).all())

            well_dict = {well.well_id: well.id for well in wells}
            gdf['well_id'] = gdf['well_id'].astype(str)
            gdf['well_id'] = gdf['well_id'].map(well_dict)
            gdf.dropna(subset=['time', 'value'], inplace=True)
            for row in gdf.itertuples():
                measurement = Measurement(well_id=int(row.well_id),
                                          variable_id=int(row.variable_id),
                                          ts_time=row.time,
                                          ts_value=float(row.value),
                                          ts_format=time_format
                                          )
                session.add(measurement)
            session.commit()
            session.close()
            response = {'success': 'success'}
        else:
            response = {'error': 'There were null values in the data. Please fix the data and upload again.'}
    except Exception as e:
        session.close()
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}

    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    return response


def get_timeseries(well_id: str, variable_id: int) -> List:
    """
    Generate Highcharts appropriate timeseries list

    Args:
        well_id: Well Id string as stored in the Measurement Table
        variable_id: Variable Id integer as stored in the variable/measurement table

    Returns:
        list of lists with utc time in milliseconds and measurement value
    """
    session = get_session_obj()
    well_id = well_id.split('.')[1]
    ts_obj = session.query(Measurement).filter(Measurement.well_id == well_id,
                                               Measurement.variable_id == variable_id).all()
    timeseries = sorted([[calendar.timegm(datetime.strptime(obj.ts_time, obj.ts_format).utctimetuple())*1000,
                          obj.ts_value] for obj in ts_obj])
    session.close()
    return timeseries


def get_well_obs(aquifer_id: int, variable_id: int) -> Dict:
    """
    Get a Dict containing the Count of Measurements for each well in an aquifer

    Args:
        aquifer_id: Aquifer Id Integer as listed in the database
        variable_id: Variable Id Integer as listed in the database

    Returns:
        Dictionary of well ids as keys and variable measurement count as values.
        Will be used for the slider in the region map.
    """
    session = get_session_obj()
    wells_list = [r.id for r in session.query(Well.id).filter(Well.aquifer_id == aquifer_id).distinct()]
    m_query = (session.query(Measurement.well_id,
                             func.count(Measurement.ts_value).label('obs'))
               .group_by(Measurement.well_id)
               .filter(Measurement.well_id.in_(wells_list),
                       Measurement.variable_id == variable_id))
    obs_dict = {w.well_id: w.obs for w in m_query}
    zero_obs_wells = set(wells_list) - set(obs_dict.keys())
    for well in zero_obs_wells:
        obs_dict[well] = 0
    return obs_dict


def get_well_info(well_id: str) -> Dict:
    """
    Get well info for chart metadata

    Args:
        well_id: Well Id String from the popup

    Returns:
        A Dictionary with Well metadata that will be showed in the timeseries chart
    """
    session = get_session_obj()
    well_id = well_id.split('.')[1]
    well = session.query(Well).filter(Well.id == well_id).first()
    json_dict = {"id": well.id,
                 "well_name": well.well_name,
                 "gse": well.gse,
                 "attr_dict": json.dumps(well.attr_dict)
                 }

    session.close()
    return json_dict


def create_outlier(well_id: str) -> bool:
    """
    Set outlier based on selected well id

    Args:
        well_id: Well Id string from popup click

    Returns:
        Outlier boolean of the well
    """
    session = get_session_obj()
    well_id = well_id.split('.')[1]
    well_obj = session.query(Well).filter(Well.id == well_id).first()
    set_value = not well_obj.outlier
    well_obj.outlier = set_value
    session.commit()
    session.flush()
    session.close()
    return set_value


def get_wms_datasets(aquifer_name: str, variable_id: str, region_id: str) -> List:
    """
    Get a list of all available wms datasets for given region, aquifer, and variable

    Args:
        aquifer_name: Selected Aquifer Name from the Region Map page
        variable_id: Selected Variable Id from the Region Map page
        region_id: Selected region from the Region map page

    Returns:
        List of lists Thredds WMS Urls and File Names
    """
    catalog = app.get_spatial_dataset_service('primary_thredds', as_engine=True)
    aquifer_name = aquifer_name.replace(" ", "_")
    c = Crawl(catalog.catalog_url)
    file_str = f'{region_id}/{aquifer_name}/{aquifer_name}_{variable_id}'
    urls = [[s.get("url"), d.name] for d in c.datasets for s in d.services
            if s.get("service").lower() == "wms" and file_str in s.get("url")]

    return urls


def get_wms_metadata(aquifer_name: str, file_name: str, region_id: str) -> Tuple[int, int]:
    """
    Get min and max for selected wms layer

    Args:
        aquifer_name: Selected Aquifer Name
        file_name: Selected netcdf file name
        region_id: Selected Region Id

    Returns:
        The min and max value for a selected interpolation netcdf file
    """
    thredds_directory = app.get_custom_setting('gw_thredds_directoy')
    # aquifer_dir = os.path.join(thredds_directory, str(region_id), str(aquifer_obj[1]))
    aquifer_name = aquifer_name.replace(" ", "_")
    file_path = os.path.join(thredds_directory, str(region_id), aquifer_name, file_name)
    # for val in rename_ds['Week'].values:
    #     print(datetime.strptime(f'2019 {val - 1}  0', "%Y %W %w").toordinal())

    ds = xr.open_dataset(file_path)
    range_min = int(ds.tsvalue.min().values)
    range_max = int(ds.tsvalue.max().values)
    return range_min, range_max


def get_geoserver_status() -> dict:
    """
    Get GeoServer status in the app. Query using the Tethys gs_config wrapper to check if the workspace, store,
    and layers exist for the app within the GeoServer.

    Returns:
        A dict with workspace, store, and layer status
    """
    gs_engine = app.get_spatial_dataset_service('primary_geoserver', as_engine=True)
    workspaces = gs_engine.list_workspaces()['result']
    ws_name = 'gwdm'
    store_name = 'postgis'
    if ws_name in workspaces:
        workspace_status = 'Configured'
        stores = gs_engine.list_stores(workspace=ws_name)['result']
        if store_name in stores:
            store_status = 'Configured'
            layers = gs_engine.list_resources(store=store_name, workspace=ws_name)['result']
            if all(x in layers for x in ['well', 'aquifer', 'region']):
                layer_status = 'Configured'
            else:
                layer_status = 'Not Setup'
        else:
            store_status = 'Not Setup'
            layer_status = 'Not Setup'
    else:
        workspace_status = 'Not Setup'
        store_status = 'Not Setup'
        layer_status = 'Not Setup'

    status = {'workspace_status': workspace_status,
              'store_status': store_status,
              'layer_status': layer_status}
    return status


def get_thredds_status() -> dict:
    """
    Get Thredds status in the app. Check if the relevant directory exists.

    Returns:
        A dict with the thredds groundwater directory status
    """

    thredds_directory = app.get_custom_setting('gw_thredds_directoy')
    if os.path.exists(thredds_directory):
        directory_status = 'Configured'
    else:
        directory_status = 'Not Setup'

    status = {'directory_status': directory_status}
    return status


def delete_measurements(region: str, aquifer: str, variable: str) -> dict:
    """
    Delete measurements from the database for a selected region, aquifer, and variable

    Args:
        region: Region ID string from ajax request
        aquifer: Aquifer ID String. options: 'all' or a specific aquifer id
        variable: Variable ID String. options: 'all' or specific variable id

    Returns:
        JSON Dictionary indicating whether the operation succeeded
    """
    response = {}
    try:
        region_id = int(region)
        session = get_session_obj()
        if aquifer == 'all':
            aquifers_list = get_region_aquifers_list(region_id)
            aquifers = [aqf[1] for aqf in aquifers_list]
        elif ',' in aquifer:
            aquifers = [int(aqf) for aqf in aquifer.split(',')]
        else:
            aquifers = [int(aquifer)]

        if variable == 'all':
            variables_list = get_region_variables_list(region_id)
            variables = [var[1] for var in variables_list]
        elif ',' in variable:
            variables = [int(var) for var in variable.split(',')]
        else:
            variables = [int(variable)]

        measurements_query = (session.query(Measurement)
                              .join(Well, Measurement.well_id == Well.id)
                              .filter(Measurement.variable_id.in_(variables),
                                      Well.aquifer_id.in_(aquifers))
                              ).all()

        for meas in measurements_query:
            session.delete(meas)
        session.commit()
        session.close()
        response['success'] = 'success'
    except Exception as e:
        response['error'] = str(e)
    return response


def delete_bulk_wells(region: str, aquifer: str) -> dict:
    """
    Bulk Delete Wells in an Aquifer

    Args:
        region: Region ID in the database
        aquifer: Aquifer ID in the database. options: all or aquifer id

    Returns:
        JSON response indicating whether the wells were deleted
    """
    response = {}
    try:
        region_id = int(region)
        if aquifer == 'all':
            aquifers_list = get_region_aquifers_list(region_id)
            aquifers = [aqf[1] for aqf in aquifers_list]
        elif ',' in aquifer:
            aquifers = [int(aqf) for aqf in aquifer.split(',')]
        else:
            aquifers = [int(aquifer)]
        session = get_session_obj()
        wells_query = session.query(Well).filter(Well.aquifer_id.in_(aquifers)).all()
        for well in wells_query:
            session.delete(well)
        session.commit()
        session.close()
        response['success'] = 'success'
    except Exception as e:
        response['error'] = str(e)

    return response


def process_nc_files(region: int, aquifer: str, variable: str, file: Any) -> Dict:
    """
    Upload NetCDF files to the Thredds Directory

    Args:
        region: Region ID as listed in the Database
        aquifer: Aquifer Name as listed in the Database
        variable: Variable ID as listed in the Database
        file: File(s) to upload

    Returns:
        JSON Response indicating if the files were uploaded
    """
    response = {}
    try:
        thredds_directory = app.get_custom_setting('gw_thredds_directoy')
        region_dir = os.path.join(thredds_directory, str(region))
        aquifer = aquifer.replace(" ", "_")
        if not os.path.exists(region_dir):
            os.makedirs(region_dir)
        aquifer_dir = os.path.join(region_dir, str(aquifer))
        if not os.path.exists(aquifer_dir):
            os.makedirs(aquifer_dir)
        for f in file:
            f_name = f'{aquifer}_{variable}_{time.time()}.nc'
            f_path = os.path.join(aquifer_dir, f_name)
            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())
        response['success'] = 'success'
    except Exception as e:
        response['error'] = str(e)
    return response


def delete_bulk_rasters(region: str, aquifer: str, variable: str, raster: str) -> Dict:
    """
    Delete Rasters from Thredds Directory

    Args:
        region: Region ID String as listed in the database
        aquifer: Aquifer Name String as listed in the database
        variable: Variable String as listed in the database
        raster: Raster File String as listed in Thredds

    Returns:
        JSON Dict indicating if the files were deleted
    """
    response = {}
    try:
        region_id = int(region)
        all_aquifers = 'All Aquifers'
        all_str = 'all'
        if aquifer == all_aquifers:
            aquifers_list = get_region_aquifers_list(region_id)
            aquifers = [aqf[0].replace(" ", "_") for aqf in aquifers_list]
        elif ',' in aquifer:
            aquifers = [aqf.replace(" ", "_") for aqf in aquifer.split(',')]
        else:
            aquifers = [aquifer.replace(" ", "_")]

        if variable == all_str:
            variables_list = get_region_variables_list(region_id)
            variables = [v[1] for v in variables_list]
        elif ',' in aquifer:
            variables = [v for v in variable.split(',')]
        else:
            variables = [variable]

        thredds_directory = app.get_custom_setting('gw_thredds_directoy')
        region_dir = os.path.join(thredds_directory, str(region_id))
        if aquifer == all_aquifers and variable == all_str and raster == all_str:
            shutil.rmtree(region_dir)
        elif aquifer != all_aquifers:
            for aqf in aquifers:
                for var in variables:
                    if raster == all_str:
                        raster_files = glob.glob(os.path.join(region_dir, aqf, f'*_{var}_*.nc'))
                        for r_file in raster_files:
                            os.remove(r_file)
                    else:
                        if ',' in raster:
                            rasters = [r for r in raster.split(',')]
                            for rast in rasters:
                                r_file = os.path.join(region_dir, aqf, rast)
                                os.remove(r_file)
                        else:
                            r_file = os.path.join(region_dir, aqf, raster)
                            os.remove(r_file)
        elif variable != all_str and aquifer == all_aquifers:
            for aqf in aquifers:
                raster_files = glob.glob(os.path.join(region_dir, aqf, f'*_{variable}_*.nc'))
                for r_file in raster_files:
                    os.remove(r_file)

    except Exception as e:
        response['error'] = str(e)
    response['success'] = 'success'
    return response


def delete_region_thredds_dir(region_id: str) -> str:
    """
    Delete the region directory in the Thredds public folder

    Args:
        region_id: Selected Region Id

    Returns:
        Success message on region deleted
    """
    thredds_directory = app.get_custom_setting('gw_thredds_directoy')
    region_path = os.path.join(thredds_directory, region_id)
    if os.path.exists(region_path):
        shutil.rmtree(region_path)
        status = 'success'
        return status


def date_format_validator(date_format: str) -> bool:
    """
    Validate the date format entered by the user
    Args:
        date_format: Date Format String

    Returns:
        Boolean indicating if the format is good
    """
    test_date = '12-31-1999'
    try:
        valid_date = datetime.strptime(test_date, '%m-%d-%Y').strftime(date_format)
        if valid_date == date_format or len(valid_date) == 0:
            is_valid = False
        else:
            is_valid = True
    except Exception as e:
        print(e)
        is_valid = False

    return is_valid
