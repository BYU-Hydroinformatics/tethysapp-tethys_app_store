from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, PersistentStoreConnectionSetting, CustomSetting


class Newgrace(TethysAppBase):
    """
    Tethys app class for Newgrace.
    """

    name = 'GRACE Groundwater Subsetting Tool'
    index = 'newgrace:home'
    icon = 'newgrace/images/logo.jpg'
    package = 'newgrace'
    root_url = 'newgrace'
    color = '#222222'
    description = 'The GRACE application is a visualization tool for GRACE global satellite data. It also provides visualization for global surface water, soil moisture, and groundwater data.'
    tags = '&quot;Hydrology&quot;, &quot;Groundwater&quot;'
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
                url='newgrace',
                controller='newgrace.controllers.home'
            ),
            UrlMap(
                name='global-map',
                url='global-map',
                controller='newgrace.controllers.global_map'
            ),

            UrlMap(
                name='update-global-files',
                url='newgrace/update-global-files',
                controller='newgrace.controllers.update_global_files'
            ),
            UrlMap(
                name='region',
                url='region',
                controller='newgrace.controllers.region'
            ),
            UrlMap(
                name='add-region',
                url='add-region',
                controller='newgrace.controllers.add_region'
            ),
            UrlMap(
                name='get-plot-global',
                url='global-map/get-plot-global',
                controller='newgrace.ajax_controllers.get_plot_global'
            ),
            UrlMap(
                name='get-plot-reg-pt',
                url='region/get-plot-reg-pt',
                controller='newgrace.ajax_controllers.get_plot_reg_pt'
            ),


            UrlMap(name='grcfo-update-check-ajax',
                   url='newgrace/update-global-files/grcfo-update-check',
                   controller='newgrace.update_global_data.grcfo_update_check'
            ),
            UrlMap(name='update-grace-files-ajax',
                   url='newgrace/update-grace-files',
                   controller='newgrace.update_global_data.update_grace_files'
            ),
            UrlMap(name='download-gldas-data-ajax',
                   url='newgrace/download-gldas-data',
                   controller='newgrace.update_global_data.download_gldas_data'
            ),
            UrlMap(name='update-other-soulution-files-ajax',
                   url='newgrace/update-other-soulution-files',
                   controller='newgrace.update_global_data.update_other_solution_files'
            ),


            UrlMap(name='add-region-ajax',
                   url='newgrace/add-region/submit',
                   controller='newgrace.ajax_controllers.region_add'
            ),
            UrlMap(name='initial-processing-ajax',
                   url='newgrace/add-region/initial',
                   controller='newgrace.ajax_controllers.subset_initial_processing'
            ),
            UrlMap(name='jpl-tot-ajax',
                   url='newgrace/add-region/jpl-tot',
                   controller='newgrace.ajax_controllers.subset_jpl_tot'
            ),
            UrlMap(name='jpl-gw-ajax',
                   url='newgrace/add-region/jpl-gw',
                   controller='newgrace.ajax_controllers.subset_jpl_gw'
            ),
            UrlMap(name='csr-tot-ajax',
                   url='newgrace/add-region/csr-tot',
                   controller='newgrace.ajax_controllers.subset_csr_tot'
            ),
            UrlMap(name='csr-gw-ajax',
                   url='newgrace/add-region/csr-gw',
                   controller='newgrace.ajax_controllers.subset_csr_gw'
            ),
            UrlMap(name='gfz-tot-ajax',
                   url='newgrace/add-region/gfz-tot',
                   controller='newgrace.ajax_controllers.subset_gfz_tot'
            ),
            UrlMap(name='gfz-gw-ajax',
                   url='newgrace/add-region/gfz-gw',
                   controller='newgrace.ajax_controllers.subset_gfz_gw'
            ),
            UrlMap(name='avg-tot-ajax',
                   url='newgrace/add-region/avg-tot',
                   controller='newgrace.ajax_controllers.subset_avg_tot'
            ),
            UrlMap(name='avg-gw-ajax',
                   url='newgrace/add-region/avg-gw',
                   controller='newgrace.ajax_controllers.subset_avg_gw'
            ),
            UrlMap(name='sw-ajax',
                   url='newgrace/add-region/sw',
                   controller='newgrace.ajax_controllers.subset_sw'
            ),
            UrlMap(name='soil-ajax',
                   url='newgrace/add-region/soil',
                   controller='newgrace.ajax_controllers.subset_soil'
            ),
            UrlMap(name='cleanup-ajax',
                   url='newgrace/add-region/cleanup',
                   controller='newgrace.ajax_controllers.subset_cleanup'
            ),
            UrlMap(name='update-ajax',
                   url='newgrace/add-region/update',
                   controller='newgrace.ajax_controllers.subset_update'
            ),



            UrlMap(
                name='add-thredds-server',
                url='add-thredds-server',
                controller='newgrace.controllers.add_thredds_server'
            ),
            UrlMap(name='add-thredds-server-ajax',
                   url='newgrace/add-thredds-server/submit',
                   controller='newgrace.ajax_controllers.thredds_server_add'
            ),
            UrlMap(name='update-thredds-servers-ajax',
                   url='newgrace/manage-thredds-servers/submit',
                   controller='newgrace.ajax_controllers.thredds_server_update'
            ),
            UrlMap(name='delete-thredds-server-ajax',
                   url='newgrace/manage-thredds-servers/delete',
                   controller='newgrace.ajax_controllers.thredds_server_delete'
            ),
            UrlMap(
                name='manage-regions',
                url='manage-regions',
                controller='newgrace.controllers.manage_regions'
            ),
            UrlMap(name='manage-regions-table',
                   url='newgrace/manage-regions/table',
                   controller='newgrace.controllers.manage_regions_table'
            ),
            UrlMap(name='delete-regions-ajax',
                   url='newgrace/manage-regions/delete',
                   controller='newgrace.ajax_controllers.region_delete'
            ),
            UrlMap(
                name='manage-thredds-servers',
                url='manage-thredds-servers',
                controller='newgrace.controllers.manage_thredds_servers'
            ),
            UrlMap(name='manage-thredds-servers-table',
                   url='newgrace/manage-thredds-servers/table',
                   controller='newgrace.controllers.manage_thredds_servers_table'
            ),
            UrlMap(name='api_get_point_values',
                   url='newgrace/api/GetPointValues',
                   controller='newgrace.api.api_get_point_values'),

        )

        return url_maps

    def custom_settings(self):
        custom_settings = (
            CustomSetting(
                name='Local Thredds Folder Path',
                type=CustomSetting.TYPE_STRING,
                description='Path to Global NetCDF Directory (Local Folder Mounted to Thredds Docker)',
                required=True,
            ),
            CustomSetting(
                name='Thredds wms URL',
                type=CustomSetting.TYPE_STRING,
                description='URL to thredds Global Directory folder (make sure it paths to the folder and not a specific layer)',
                required=True,
            ),
        )
        return custom_settings

    def persistent_store_settings(self):

        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='gracefo_db',
                description='For storing Region and Thredds metadata',
                required=True,
                initializer='newgrace.model.init_gracefo_db',
                spatial=False,
            ),
        )

        return ps_settings
