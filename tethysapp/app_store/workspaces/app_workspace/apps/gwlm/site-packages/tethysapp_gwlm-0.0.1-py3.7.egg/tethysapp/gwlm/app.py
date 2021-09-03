from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, SpatialDatasetServiceSetting, CustomSetting
from tethys_sdk.base import TethysAppBase, url_map_maker


class Gwlm(TethysAppBase):
    """
    Tethys app class for Ground Water Level Mapper.
    """

    name = 'Groundwater Data Mapper'
    index = 'gwlm:home'
    icon = 'gwlm/images/gw_logo.png'
    package = 'gwlm'
    root_url = 'gwlm'
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
                url='gwlm',
                controller='gwlm.controllers.home'
            ),
            UrlMap(
                name='config',
                url='gwlm/config',
                controller='gwlm.controllers.config'
            ),
            UrlMap(
                name='metrics',
                url='gwlm/metrics',
                controller='gwlm.controllers.metrics'
            ),
            UrlMap(
                name='interpolation',
                url='gwlm/interpolation',
                controller='gwlm.controllers.interpolation'
            ),
            UrlMap(
                name='interpolation-submit',
                url='gwlm/interpolation/submit',
                controller='gwlm.controllers_ajax.interpolate'
            ),
            UrlMap(
                name='interpolation-aquifers',
                url='gwlm/interpolation/get-aquifers',
                controller='gwlm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='run-dask',
                url='gwlm/dask/add/{job_type}',
                controller='gwlm.controllers.run_job'
            ),
            UrlMap(
                name='jobs-table',
                url='gwlm/dask/jobs_table',
                controller='gwlm.controllers.jobs_table'
            ),
            UrlMap(
                name='result',
                url='gwlm/dask/result/{job_id}',
                controller='gwlm.controllers.result'
            ),
            UrlMap(
                name='error_message',
                url='gwlm/dask/error',
                controller='gwlm.controllers.error_message'
            ),
            UrlMap(
                name='region-map',
                url='gwlm/region-map',
                controller='gwlm.controllers.region_map'
            ),
            UrlMap(
                name='region-map-ts',
                url='gwlm/region-map/get-timeseries',
                controller='gwlm.controllers_ajax.region_timeseries'
            ),
            UrlMap(
                name='region-map-well-obs',
                url='gwlm/region-map/get-well-obs',
                controller='gwlm.controllers_ajax.region_well_obs'
            ),
            UrlMap(
                name='region-map-wms-datasets',
                url='gwlm/region-map/get-wms-datasets',
                controller='gwlm.controllers_ajax.region_wms_datasets'
            ),
            UrlMap(
                name='region-map-wms-metadata',
                url='gwlm/region-map/get-wms-metadata',
                controller='gwlm.controllers_ajax.region_wms_metadata'
            ),
            UrlMap(
                name='region-map-outlier',
                url='gwlm/region-map/set-outlier',
                controller='gwlm.controllers_ajax.set_outlier'
            ),
            UrlMap(
                name='add-region',
                url='gwlm/add-region',
                controller='gwlm.controllers.add_region'
            ),
            UrlMap(
                name='add-region-ajax',
                url='gwlm/add-region/submit',
                controller='gwlm.controllers_ajax.region_add'
            ),
            UrlMap(
                name='update-region',
                url='gwlm/update-region',
                controller='gwlm.controllers.update_region'
            ),
            UrlMap(
                name='update-region-tabulator',
                url='gwlm/update-region/tabulator',
                controller='gwlm.controllers_ajax.region_tabulator'
            ),
            UrlMap(
                name='update-region-ajax',
                url='gwlm/update-region/update',
                controller='gwlm.controllers_ajax.region_update'
            ),
            UrlMap(
                name='delete-region-ajax',
                url='gwlm/update-region/delete',
                controller='gwlm.controllers_ajax.region_delete'
            ),
            UrlMap(
                name='add-aquifer',
                url='gwlm/add-aquifer',
                controller='gwlm.controllers.add_aquifer'
            ),
            UrlMap(
                name='update-aquifer',
                url='gwlm/update-aquifer',
                controller='gwlm.controllers.update_aquifer'
            ),
            UrlMap(
                name='update-aquifer-tabulator',
                url='gwlm/update-aquifer/tabulator',
                controller='gwlm.controllers_ajax.aquifer_tabulator'
            ),
            UrlMap(
                name='update-aquifer-ajax',
                url='gwlm/update-aquifer/update',
                controller='gwlm.controllers_ajax.aquifer_update'
            ),
            UrlMap(
                name='delete-aquifer-ajax',
                url='gwlm/update-aquifer/delete',
                controller='gwlm.controllers_ajax.aquifer_delete'
            ),
            UrlMap(
                name='get-aquifer-attributes',
                url='gwlm/add-aquifer/get-attributes',
                controller='gwlm.controllers_ajax.get_shp_attributes'
            ),
            UrlMap(
                name='add-aquifer-ajax',
                url='gwlm/add-aquifer/submit',
                controller='gwlm.controllers_ajax.aquifer_add'
            ),
            UrlMap(
                name='add-wells',
                url='gwlm/add-wells',
                controller='gwlm.controllers.add_wells'
            ),
            UrlMap(
                name='get-wells-attributes',
                url='gwlm/add-wells/get-attributes',
                controller='gwlm.controllers_ajax.get_well_attributes'
            ),
            UrlMap(
                name='add-wells-aquifers',
                url='gwlm/add-wells/get-aquifers',
                controller='gwlm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-wells-ajax',
                url='gwlm/add-wells/submit',
                controller='gwlm.controllers_ajax.wells_add'
            ),
            UrlMap(
                name='edit-wells',
                url='gwlm/edit-wells',
                controller='gwlm.controllers.edit_wells'
            ),
            UrlMap(
                name='edit-wells-tabulator',
                url='gwlm/edit-wells/tabulator',
                controller='gwlm.controllers_ajax.wells_tabulator'
            ),
            UrlMap(
                name='delete-well-ajax',
                url='gwlm/edit-wells/delete',
                controller='gwlm.controllers_ajax.well_delete'
            ),
            UrlMap(
                name='add-measurements',
                url='gwlm/add-measurements',
                controller='gwlm.controllers.add_measurements'
            ),
            UrlMap(
                name='add-measurements-aquifers',
                url='gwlm/add-measurements/get-aquifers',
                controller='gwlm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-measurements-aquifers',
                url='gwlm/add-measurements/get-aquifers',
                controller='gwlm.controllers_ajax.get_aquifers'
            ),
            UrlMap(
                name='add-measurements-wells',
                url='gwlm/add-measurements/get-wells',
                controller='gwlm.controllers_ajax.get_wells'
            ),
            UrlMap(
                name='get-measurements-attributes',
                url='gwlm/add-measurements/get-attributes',
                controller='gwlm.controllers_ajax.get_measurements_attributes'
            ),
            UrlMap(
                name='add-measurements-ajax',
                url='gwlm/add-measurements/submit',
                controller='gwlm.controllers_ajax.measurements_add'
            ),
            UrlMap(
                name='add-variable',
                url='gwlm/add-variable',
                controller='gwlm.controllers.add_variable'
            ),
            UrlMap(
                name='update-variable',
                url='gwlm/update-variable',
                controller='gwlm.controllers.update_variable'
            ),
            UrlMap(
                name='update-variable-tabulator',
                url='gwlm/update-variable/tabulator',
                controller='gwlm.controllers_ajax.variable_tabulator'
            ),
            UrlMap(
                name='delete-variable-ajax',
                url='gwlm/update-variable/delete',
                controller='gwlm.controllers_ajax.variable_delete'
            ),
            UrlMap(
                name='update-variable-ajax',
                url='gwlm/update-variable/update',
                controller='gwlm.controllers_ajax.variable_update'
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
                initializer='gwlm.model.init_db',
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

