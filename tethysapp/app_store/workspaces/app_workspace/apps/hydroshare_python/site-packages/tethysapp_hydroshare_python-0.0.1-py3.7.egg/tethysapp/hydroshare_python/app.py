from tethys_sdk.base import TethysAppBase, url_map_maker


class HydrosharePython(TethysAppBase):
    """
    Tethys app class for Hydroshare library.
    """

    name = 'HydroShare Python API Demonstration'
    index = 'hydroshare_python:home'
    icon = 'hydroshare_python/images/icon.gif'
    package = 'hydroshare_python'
    root_url = 'hydroshare-python'
    color = '#008000'
    description = 'A web app to demonstrate the use of hs_restclient and generate operations available in the HydroShare website. This app is more of a tutorial and designed to educate a programmer to learn how Python APIs work.'
    tags = 'Python library, Hydroshare'
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
                url='hydroshare-python',
                controller='hydroshare_python.controllers.home'
            ),
            UrlMap(
                name='get_file',
                url='hydroshare-python/get_file',
                controller='hydroshare_python.controllers.get_file'
            ),
            UrlMap(
                name='add_file',
                url='hydroshare-python/add_file',
                controller='hydroshare_python.controllers.add_file'
            ),
            UrlMap(
                name='delete_resource',
                url='hydroshare-python/delete_resource',
                controller='hydroshare_python.controllers.delete_resource'
            ),
            UrlMap(
                name='delete_file',
                url='hydroshare-python/delete_file',
                controller='hydroshare_python.controllers.delete_file'
            ),
            UrlMap(
                name='viewer',
                url='hydroshare-python/viewer',
                controller='hydroshare_python.controllers.viewer'
            ),
            UrlMap(
                name='download_file',
                url='hydroshare-python/download_file',
                controller='hydroshare_python.controllers.download_file'
            ),
            UrlMap(
                name='mapview',
                url='hydroshare-python/mapview',
                controller='hydroshare_python.controllers.mapview'
            ),
            UrlMap(
                name='filev',
                url='hydroshare-python/filev',
                controller='hydroshare_python.controllers.filev'
            ),
            UrlMap(
                name='metadata',
                url='hydroshare-python/metadata',
                controller='hydroshare_python.controllers.metadata'
            ),
            UrlMap(
                name='download_resource',
                url='hydroshare-python/download_resource',
                controller='hydroshare_python.controllers.download_resource'
            ),
            UrlMap(
                name='change_public',
                url='hydroshare-python/change_public',
                controller='hydroshare_python.controllers.change_public'
            ),
            UrlMap(
                name='create_folder',
                url='hydroshare-python/create_folder',
                controller='hydroshare_python.controllers.create_folder'
            ),
            UrlMap(
                name='tutorial',
                url='hydroshare-python/tuorial',
                controller='hydroshare_python.controllers.tutorial'
            ),
            UrlMap(
                name='featurespage',
                url='hydroshare-python/featurespage',
                controller='hydroshare_python.controllers.featurespage'
            ),
            UrlMap(
                name='getfile_metadata',
                url='hydroshare-python/getfile_metadata',
                controller='hydroshare_python.controllers.getfile_metadata'
            ),
            UrlMap(
                name='deletefolder',
                url='hydroshare-python/deletefolder',
                controller='hydroshare_python.controllers.deletefolder'
            ),
            UrlMap(
                name='tethys',
                url='hydroshare-python/tethys',
                controller='hydroshare_python.controllers.tethys'
            ),
            UrlMap(
                name='boundingbox',
                url='hydroshare-python/boundingbox',
                controller='hydroshare_python.controllers.boundingbox'
            ),
            UrlMap(
                name='random',
                url='hydroshare-python/random',
                controller='hydroshare_python.controllers.random'
            ),
            UrlMap(
                name='geoserver',
                url='hydroshare-python/geoserver',
                controller='hydroshare_python.controllers.geoserver'
            ),
            UrlMap(
                name='loading',
                url='hydroshare-python/loading',
                controller='hydroshare_python.controllers.loading'
            ),

            
        )

        return url_maps