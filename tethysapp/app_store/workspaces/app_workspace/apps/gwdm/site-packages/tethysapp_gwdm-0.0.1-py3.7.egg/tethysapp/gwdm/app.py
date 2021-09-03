from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, SpatialDatasetServiceSetting, CustomSetting
from tethys_sdk.base import TethysAppBase, url_map_maker


class Gwdm(TethysAppBase):
    """
    Tethys app class for Ground Water Level Mapper.
    """

    name = 'Groundwater Data Mapper'
    index = 'gwdm:home'
    icon = 'gwdm/images/gw_logo.png'
    package = 'gwdm'
    root_url = 'gwdm'
    color = '#2c3e50'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='gwdm',
                controller='gwdm.controllers.home'
            ),
            UrlMap(
                name='config',
                url='gwdm/config',
                controller='gwdm.controllers.config'
            ),
            UrlMap(
                name='metrics',
                url='gwdm/metrics',
                controller='gwdm.controllers.metrics'
            ),
            UrlMap(
                name='interpolation',
                url='gwdm/interpolation',
                controller='gwdm.controllers.interpolation'
            ),
            UrlMap(
                name='interpolation-submit',
                url='gwdm/interpolation/submit',
                controller='gwdm.controllers_ajax.interpolate'
            ),
            UrlMap(
                name='interpolation-aquifers',
                url='gwdm/interpolation/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='run-dask',
                url='gwdm/dask/add/{job_type}',
                controller='gwdm.controllers.run_job'
            ),
            UrlMap(
                name='jobs-table',
                url='gwdm/dask/jobs_table',
                controller='gwdm.controllers.jobs_table'
            ),
            UrlMap(
                name='result',
                url='gwdm/dask/result/{job_id}',
                controller='gwdm.controllers.result'
            ),
            UrlMap(
                name='error_message',
                url='gwdm/dask/error',
                controller='gwdm.controllers.error_message'
            ),
            UrlMap(
                name='region-map',
                url='gwdm/region-map',
                controller='gwdm.controllers.region_map'
            ),
            UrlMap(
                name='region-map-ts',
                url='gwdm/region-map/get-timeseries',
                controller='gwdm.controllers_ajax.region_timeseries'
            ),
            UrlMap(
                name='region-map-well-obs',
                url='gwdm/region-map/get-well-obs',
                controller='gwdm.controllers_ajax.region_well_obs'
            ),
            UrlMap(
                name='region-map-wms-datasets',
                url='gwdm/region-map/get-wms-datasets',
                controller='gwdm.controllers_ajax.region_wms_datasets'
            ),
            UrlMap(
                name='region-map-wms-metadata',
                url='gwdm/region-map/get-wms-metadata',
                controller='gwdm.controllers_ajax.region_wms_metadata'
            ),
            UrlMap(
                name='region-map-outlier',
                url='gwdm/region-map/set-outlier',
                controller='gwdm.controllers_ajax.set_outlier'
            ),
            UrlMap(
                name='add-region',
                url='gwdm/add-region',
                controller='gwdm.controllers.add_region'
            ),
            UrlMap(
                name='add-region-ajax',
                url='gwdm/add-region/submit',
                controller='gwdm.controllers_ajax.region_add'
            ),
            UrlMap(
                name='update-region',
                url='gwdm/update-region',
                controller='gwdm.controllers.update_region'
            ),
            UrlMap(
                name='update-region-tabulator',
                url='gwdm/update-region/tabulator',
                controller='gwdm.controllers_ajax.region_tabulator'
            ),
            UrlMap(
                name='update-region-ajax',
                url='gwdm/update-region/update',
                controller='gwdm.controllers_ajax.region_update'
            ),
            UrlMap(
                name='delete-region-ajax',
                url='gwdm/update-region/delete',
                controller='gwdm.controllers_ajax.region_delete'
            ),
            UrlMap(
                name='add-aquifer',
                url='gwdm/add-aquifer',
                controller='gwdm.controllers.add_aquifer'
            ),
            UrlMap(
                name='update-aquifer',
                url='gwdm/update-aquifer',
                controller='gwdm.controllers.update_aquifer'
            ),
            UrlMap(
                name='update-aquifer-tabulator',
                url='gwdm/update-aquifer/tabulator',
                controller='gwdm.controllers_ajax.aquifer_tabulator'
            ),
            UrlMap(
                name='update-aquifer-ajax',
                url='gwdm/update-aquifer/update',
                controller='gwdm.controllers_ajax.aquifer_update'
            ),
            UrlMap(
                name='delete-aquifer-ajax',
                url='gwdm/update-aquifer/delete',
                controller='gwdm.controllers_ajax.aquifer_delete'
            ),
            UrlMap(
                name='get-aquifer-attributes',
                url='gwdm/add-aquifer/get-attributes',
                controller='gwdm.controllers_ajax.get_shp_attributes'
            ),
            UrlMap(
                name='add-aquifer-ajax',
                url='gwdm/add-aquifer/submit',
                controller='gwdm.controllers_ajax.aquifer_add'
            ),
            UrlMap(
                name='add-wells',
                url='gwdm/add-wells',
                controller='gwdm.controllers.add_wells'
            ),
            UrlMap(
                name='get-wells-attributes',
                url='gwdm/add-wells/get-attributes',
                controller='gwdm.controllers_ajax.get_well_attributes'
            ),
            UrlMap(
                name='add-wells-aquifers',
                url='gwdm/add-wells/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-wells-ajax',
                url='gwdm/add-wells/submit',
                controller='gwdm.controllers_ajax.wells_add'
            ),
            UrlMap(
                name='edit-wells',
                url='gwdm/edit-wells',
                controller='gwdm.controllers.edit_wells'
            ),
            UrlMap(
                name='edit-wells-aquifers',
                url='gwdm/edit-wells/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='edit-wells-tabulator',
                url='gwdm/edit-wells/tabulator',
                controller='gwdm.controllers_ajax.wells_tabulator'
            ),
            UrlMap(
                name='delete-well-ajax',
                url='gwdm/edit-wells/delete',
                controller='gwdm.controllers_ajax.well_delete'
            ),
            UrlMap(
                name='delete-wells',
                url='gwdm/delete-wells',
                controller='gwdm.controllers.delete_wells'
            ),
            UrlMap(
                name='delete-wells-aquifers',
                url='gwdm/delete-wells/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='delete-wells-submit',
                url='gwdm/delete-wells/submit',
                controller='gwdm.controllers_ajax.bulk_delete_wells'
            ),
            UrlMap(
                name='add-measurements',
                url='gwdm/add-measurements',
                controller='gwdm.controllers.add_measurements'
            ),
            UrlMap(
                name='add-measurements-aquifers',
                url='gwdm/add-measurements/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-measurements-date-format',
                url='gwdm/add-measurements/check-date-format',
                controller='gwdm.controllers_ajax.validate_date_format'
            ),
            UrlMap(
                name='add-measurements-aquifers',
                url='gwdm/add-measurements/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-measurements-wells',
                url='gwdm/add-measurements/get-wells',
                controller='gwdm.controllers_ajax.get_wells'
            ),
            UrlMap(
                name='get-measurements-attributes',
                url='gwdm/add-measurements/get-attributes',
                controller='gwdm.controllers_ajax.get_measurements_attributes'
            ),
            UrlMap(
                name='add-measurements-ajax',
                url='gwdm/add-measurements/submit',
                controller='gwdm.controllers_ajax.measurements_add'
            ),
            UrlMap(
                name='update-measurements',
                url='gwdm/update-measurements',
                controller='gwdm.controllers.update_measurements'
            ),
            UrlMap(
                name='update-measurements-aquifers',
                url='gwdm/update-measurements/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='update-measurements-submit',
                url='gwdm/update-measurements/submit',
                controller='gwdm.controllers_ajax.measurements_delete'
            ),
            UrlMap(
                name='add-variable',
                url='gwdm/add-variable',
                controller='gwdm.controllers.add_variable'
            ),
            UrlMap(
                name='update-variable',
                url='gwdm/update-variable',
                controller='gwdm.controllers.update_variable'
            ),
            UrlMap(
                name='update-variable-tabulator',
                url='gwdm/update-variable/tabulator',
                controller='gwdm.controllers_ajax.variable_tabulator'
            ),
            UrlMap(
                name='delete-variable-ajax',
                url='gwdm/update-variable/delete',
                controller='gwdm.controllers_ajax.variable_delete'
            ),
            UrlMap(
                name='update-variable-ajax',
                url='gwdm/update-variable/update',
                controller='gwdm.controllers_ajax.variable_update'
            ),
            UrlMap(
                name='delete-rasters',
                url='gwdm/delete-rasters',
                controller='gwdm.controllers.delete_rasters'
            ),
            UrlMap(
                name='delete-rasters-aquifers',
                url='gwdm/delete-rasters/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='rasters-wms-datasets',
                url='gwdm/delete-rasters/get-wms-datasets',
                controller='gwdm.controllers_ajax.region_wms_datasets'
            ),
            UrlMap(
                name='delete-rasters-submit',
                url='gwdm/delete-rasters/submit',
                controller='gwdm.controllers_ajax.rasters_delete'
            ),
            UrlMap(
                name='upload-rasters',
                url='gwdm/upload-rasters',
                controller='gwdm.controllers.upload_rasters'
            ),
            UrlMap(
                name='upload-rasters-aquifers',
                url='gwdm/upload-rasters/get-aquifers',
                controller='gwdm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='upload-rasters-ajax',
                url='gwdm/upload-rasters/submit',
                controller='gwdm.controllers_ajax.rasters_upload'
            ),

        )

        return url_maps

    def custom_settings(self):

        custom_settings = (
            CustomSetting(
                name='gw_thredds_directoy',
                type=CustomSetting.TYPE_STRING,
                description='Path to the Ground Water Thredds Directory',
                required=True
            ),
        )

        return custom_settings

    def persistent_store_settings(self):
        """
        Define Persistent Store Settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='gwdb',
                description='Ground Water Database',
                initializer='gwdm.model.init_db',
                required=True,
                spatial=True
            ),
        )

        return ps_settings

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name='primary_geoserver',
                description='Geoserver for app to use',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
            SpatialDatasetServiceSetting(
                name='primary_thredds',
                description='Thredds  for app to use',
                engine=SpatialDatasetServiceSetting.THREDDS,
                required=True,
            ),
        )

        return sds_settings

