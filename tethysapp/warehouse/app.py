from tethys_sdk.base import TethysAppBase, url_map_maker


class Warehouse(TethysAppBase):
    """
    Tethys app class for Warehouse.
    """

    name = 'Warehouse'
    index = 'warehouse:home'
    icon = 'warehouse/images/icon.gif'
    package = 'warehouse'
    root_url = 'warehouse'
    color = '#c0392b'
    description = 'Place a brief description of your app here.'
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
                url='warehouse',
                controller='warehouse.controllers.home'
            ),
            UrlMap(
                name='install',
                url='warehouse/install',
                controller='warehouse.controllers.install'
            ),
        )

        return url_maps
