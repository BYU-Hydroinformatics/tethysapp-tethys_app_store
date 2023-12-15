from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import CustomSetting,JSONCustomSetting,SecretCustomSetting
from tethys_sdk.permissions import Permission, PermissionGroup


class AppStore(TethysAppBase):
    """
    Tethys app class for App Store.
    """

    name = 'Tethys App Store'
    index = 'home'
    icon = 'app_store/images/appicon.png'
    package = 'app_store'
    root_url = 'app-store'
    color = '#2b7ac0'
    description = 'The Tethys App Store enables you to discover, install, manage and configure Tethys Applications '
    'for your Tethys portal.'
    tags = 'Tethys,AppStore,Conda,Github'
    enable_feedback = True
    feedback_emails = ["rohitkh@byu.edu"]

    controller_modules = ['controllers', 'notifications', 'git_install_handlers', 'scaffold_handler', ]

    def permissions(self):
        """
        Require admin to use the app.
        """
        use_app_store = Permission(
            name='use_app_store',
            description='Use the App Store'
        )

        admin = PermissionGroup(
            name='admin',
            permissions=(use_app_store,)
        )

        permissions = (admin,)

        return permissions

    def custom_settings(self):
        return (
            CustomSetting(
                name='sudo_server_pass',
                type=CustomSetting.TYPE_STRING,
                description='Sudo password for server',
                required=False
            ),
            JSONCustomSetting(
                name='stores_settings',
                description='Json Containing the different credentials for Github and Anaconda',
                required=False
            ),
            SecretCustomSetting(
                name='encryption_key',
                description='encryption_key for github token in the json',
                required=False
            ),
        )
