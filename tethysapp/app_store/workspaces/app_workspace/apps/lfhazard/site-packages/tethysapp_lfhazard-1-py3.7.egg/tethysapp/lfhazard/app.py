from tethys_sdk.base import TethysAppBase, url_map_maker


class Lfhazard(TethysAppBase):
    """
    Tethys app class for Liquefaction Hazard Lookup.
    """

    name = 'Liquefaction Hazard Parameter Lookup'
    index = 'lfhazard:home'
    icon = 'lfhazard/images/icon.gif'
    package = 'lfhazard'
    root_url = 'lfhazard'
    color = '#915F6D'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        urlmap = url_map_maker(self.root_url)

        return (
            urlmap(
                name='home',
                url=f'{self.root_url}/',
                controller='lfhazard.controllers.home'
            ),
            urlmap(
                name='getgeojson',
                url=f'{self.root_url}/getgeojson',
                controller='lfhazard.controllers.get_geojson'
            ),
            urlmap(
                name='querycsv',
                url=f'{self.root_url}/querycsv',
                controller='lfhazard.controllers.query_csv'
            ),
        )
