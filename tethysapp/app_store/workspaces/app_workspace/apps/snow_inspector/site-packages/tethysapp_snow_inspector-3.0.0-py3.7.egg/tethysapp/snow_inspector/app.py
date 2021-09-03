from tethys_sdk.base import TethysAppBase, url_map_maker


class SnowInspector(TethysAppBase):
    """
    Tethys app class for Snow Inspector.
    """

    name = 'Snow Inspector'
    index = 'snow_inspector:home'
    icon = 'snow_inspector/images/icon.gif'
    package = 'snow_inspector'
    root_url = 'snow-inspector'
    color = '#2c3e50'
    description = ('The Snow Inspector provides visual aid of a set of global snow layers '
                   'and produces a time series chart of the selected snow parameter'
                   ' anywhere in the world.')
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
                url='snow-inspector',
                controller='snow_inspector.map.map'
            ),
            UrlMap(
                name='snow_graph',
                url='snow-inspector/snow_graph',
                controller='snow_inspector.controllers.snow_graph'
            ),
            UrlMap(
                name='snow_data',
                url='snow-inspector/snow_data',
                controller='snow_inspector.modis.get_data_json'
            ),
            UrlMap(
                name='waterml',
                url='snow-inspector/waterml',
                controller='snow_inspector.modis.get_data_waterml'
            ),
            UrlMap(
                name='pixel',
                url='snow-inspector/pixel',
                controller='snow_inspector.modis.get_data_for_pixel'
            ),
            UrlMap(
                name='pixel-borders',
                url='snow-inspector/pixel-borders',
                controller='snow_inspector.modis.get_pixel_borders2'
            ),
            UrlMap(
                name='upload_to_hydroshare_ajax',
                url='snow-inspector/upload-to-hydroshare',
                controller='snow_inspector.controllers.upload_to_hydroshare'
            )
        )

        return url_maps
