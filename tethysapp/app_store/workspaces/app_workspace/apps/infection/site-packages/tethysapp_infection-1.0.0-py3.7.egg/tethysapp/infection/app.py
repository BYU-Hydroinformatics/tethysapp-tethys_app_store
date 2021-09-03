from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting
from tethys_sdk.app_settings import SpatialDatasetServiceSetting


class Infection(TethysAppBase):
    """
    Tethys app class for Infection.
    """

    name = 'Infection'
    index = 'infection:home'
    icon = 'infection/images/icon.gif'
    package = 'infection'
    root_url = 'infection'
    color = '#f39c12'
    description = 'Place a brief description of your app here.'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        urlmap = url_map_maker(self.root_url)

        return (
            # url maps to navigable pages
            urlmap(
                name='home',
                url='infection',
                controller='infection.controllers.home'
            ),

            # url maps for ajax calls
            urlmap(
                name='getChart',
                url='infection/ajax/getChart',
                controller='infection.ajax.getchart',
            ),
            urlmap(
                name='uploadShapefile',
                url='infection/ajax/uploadShapefile',
                controller='infection.ajax.uploadshapefile',
            ),
        )

    def custom_settings(self):
        return (
            CustomSetting(
                name='thredds_path',
                type=CustomSetting.TYPE_STRING,
                description="Local file path to datasets (same as used by Thredds) (e.g. /home/thredds/myDataFolder/)",
                required=True,
            ),
            CustomSetting(
                name='thredds_url',
                type=CustomSetting.TYPE_STRING,
                description="URL to the GLDAS folder on the thredds server (e.g. http://[host]/thredds/infection/)",
                required=True,
            )
        )

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        return (
            SpatialDatasetServiceSetting(
                name='geoserver',
                description='Geoserver for serving user uploaded shapefiles',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True,
            ),
        )
