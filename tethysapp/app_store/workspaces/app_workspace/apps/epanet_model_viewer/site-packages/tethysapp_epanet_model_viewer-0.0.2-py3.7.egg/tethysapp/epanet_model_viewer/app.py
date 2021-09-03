from tethys_sdk.base import TethysAppBase, url_map_maker


class EpanetModelViewer(TethysAppBase):
    """
    Tethys app class for Epanet Model Viewer.
    """

    name = 'EPANET Model Viewer'
    index = 'epanet_model_viewer:home'
    icon = 'epanet_model_viewer/images/NCIMM.png'
    package = 'epanet_model_viewer'
    root_url = 'epanet-model-viewer'
    color = '#915F6D'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        url_map = url_map_maker(self.root_url)

        url_maps = (
            url_map(name='home',
                    url='epanet-model-viewer',
                    controller='epanet_model_viewer.controllers.home'),
            url_map(name='get_epanet_model',
                    url='epanet-model-viewer/get-epanet-model',
                    controller='epanet_model_viewer.ajax_controllers.get_epanet_model'),
            url_map(name='run_epanet_model',
                    url='epanet-model-viewer/run-epanet-model',
                    controller='epanet_model_viewer.ajax_controllers.run_epanet_model'),
            url_map(name='upload_epanet_model',
                    url='epanet-model-viewer/upload-epanet-model',
                    controller='epanet_model_viewer.ajax_controllers.upload_epanet_model')
            )

        return url_maps
