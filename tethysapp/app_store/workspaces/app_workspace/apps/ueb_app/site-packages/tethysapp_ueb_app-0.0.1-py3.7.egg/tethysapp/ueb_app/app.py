from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class UebApp(TethysAppBase):
    """
    Tethys app class for Ueb App.
    """

    name = 'Utah Energy Balance Model App'
    index = 'ueb_app:home'
    icon = 'ueb_app/images/ueb.png'
    package = 'ueb_app'
    root_url = 'ueb-app'
    color = '#99ccff'
    description = 'UEB APP description'
    enable_feedback = False
    feedback_emails = []
    tags = ''

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
                    # url for model_input
                    UrlMap(name='home',
                           url='ueb-app',
                           controller='ueb_app.controllers.home'),
                    UrlMap(name='model_input',
                           url='ueb-app/model_input',
                           controller='ueb_app.controllers.model_input'),
                    UrlMap(name='model_input_submit',
                           url='ueb-app/model_input/model_input_submit',
                           controller='ueb_app.controllers.model_input_submit'),

                    # url for model_run
                    UrlMap(name='model_run',
                           url='ueb-app/model_run',
                           controller='ueb_app.controllers.model_run'),
                    UrlMap(name='model_run_submit_execution',
                           url='ueb-app/model_run/model_run_submit_execution',
                           controller='ueb_app.controllers.model_run_submit_execution'),

                    # url for check status
                    UrlMap(name='check_status',
                           url='ueb-app/check_status',
                           controller='ueb_app.controllers.check_status'),

                    # url for help
                    UrlMap(name='help_page',
                           url='ueb-app/help_page',
                           controller='ueb_app.controllers.help_page'),

                    # testing url
                    UrlMap(name='test',
                           url='ueb-app/test',
                           controller='ueb_app.controllers.test'),
                    UrlMap(name='test_submit',
                           url='ueb-app/test/test_submit',
                           controller='ueb_app.controllers.test_submit'),
        )

        return url_maps

    def custom_settings(self):
        custom_settings = (
            CustomSetting(
                name='hs_name',
                type=CustomSetting.TYPE_STRING,
                description='Global HydroShare username',
                required=True,

            ),
            CustomSetting(
                name='hs_password',
                type=CustomSetting.TYPE_STRING,
                description='Global HydroShare password',
                required=True,
            ),
            CustomSetting(
                name='hydrods_name',
                type=CustomSetting.TYPE_STRING,
                description='Global HydroDS username',
                required=True,

            ),
            CustomSetting(
                name='hydrods_password',
                type=CustomSetting.TYPE_STRING,
                description='Global HydroDS password',
                required=True,

            ),
            CustomSetting(
                name='client_id',
                type=CustomSetting.TYPE_STRING,
                description='Client ID',
                required=True,

            ),
            CustomSetting(
                name='client_secret',
                type=CustomSetting.TYPE_STRING,
                description='Client secret',
                required=True,

            ),
        )
        return custom_settings
