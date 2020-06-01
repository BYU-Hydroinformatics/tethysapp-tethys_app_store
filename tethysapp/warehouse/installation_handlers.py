import pkgutil
import inspect

from argparse import Namespace
from django.core.exceptions import ObjectDoesNotExist

from tethys_apps.base import TethysAppBase
from tethys_apps.models import CustomSetting
from tethys_apps.utilities import (get_app_settings, link_service_to_app_setting)
from tethys_cli.install_commands import (get_service_type_from_setting, get_setting_type_from_setting)
from tethys_cli.services_commands import services_list_command


def get_service_options(service_type):
    # # List existing services
    args = Namespace()

    for conf in ['spatial', 'persistent', 'wps', 'dataset']:
        setattr(args, conf, False)

    setattr(args, service_type, True)

    existing_services_list = services_list_command(args)[0]
    existing_services = []

    if(len(existing_services_list)):
        for service in existing_services_list:
            existing_services.append({
                "name": service.name,
                "id": service.id
            })
    return existing_services


def get_app_instance_from_path(paths):
    app_instance = None
    for _, modname, ispkg in pkgutil.iter_modules(paths):
        if ispkg:
            app_module = __import__('tethysapp.{}'.format(modname) + ".app", fromlist=[''])
            for name, obj in inspect.getmembers(app_module):
                # Retrieve the members of the app_module and iterate through
                # them to find the the class that inherits from AppBase.
                try:
                    # issubclass() will fail if obj is not a class
                    if (issubclass(obj, TethysAppBase)) and (obj is not TethysAppBase):
                        # Assign a handle to the class
                        AppClass = getattr(app_module, name)
                        # Instantiate app
                        app_instance = AppClass()
                        app_instance.sync_with_tethys_db()
                        # We found the app class so we're done
                        break
                except TypeError:
                    continue
    return app_instance


async def setCustomSettings(custom_settings_data, channel_layer):

    current_app = get_app_instance_from_path([custom_settings_data['app_py_path']])

    if "skip" in custom_settings_data:
        if(custom_settings_data["skip"]):
            print("Skip/NoneFound option called.")

            msg = "Custom Setting Configuration Skipped"
            if "noneFound" in custom_settings_data:
                if custom_settings_data["noneFound"]:
                    msg = "No Custom Settings Found to process."

            await channel_layer.group_send(
                "notifications",
                {
                    "type": "install_notifications",
                    "message": msg
                }
            )
            await process_settings(current_app, custom_settings_data['app_py_path'], channel_layer)
            return

    current_app_name = getattr(current_app, "name")
    custom_settings = getattr(current_app, "custom_settings")

    try:
        current_app_tethysapp_instance = TethysApp.objects.get(name=current_app_name)
    except ObjectDoesNotExist:
        print("Couldn't find app instance to get the ID to connect the settings to")
        await channel_layer.group_send(
            "notifications",
            {
                "type": "install_notifications",
                "message": "Error Setting up custom settings. Check logs for more details"
            }
        )
        return

    for setting in custom_settings():
        setting_name = getattr(setting, "name")
        actual_setting = CustomSetting.objects.get(name=setting_name, tethys_app=current_app_tethysapp_instance.id)
        if(setting_name in custom_settings_data['settings']):
            actual_setting.value = custom_settings_data['settings'][setting_name]
            actual_setting.clean()
            actual_setting.save()

    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": "Custom Settings configured."
        }
    )
    get_data_json = {
        "data": {},
        "jsHelperFunction": "customSettingConfigComplete"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )
    await process_settings(current_app, custom_settings_data['app_py_path'], channel_layer)


async def process_settings(app_instance, app_py_path, channel_layer):
    app_settings = get_app_settings(app_instance.package)

    # In the case the app isn't installed, has no settings, or it is an extension,
    # skip configuring services/settings
    if not app_settings:
        await channel_layer.group_send(
            "notifications",
            {
                "type": "install_notifications",
                "message": "No Services found to configure."
            }
        )

        return
    unlinked_settings = app_settings['unlinked_settings']

    services = []

    for setting in unlinked_settings:
        service_type = get_service_type_from_setting(setting)
        newSetting = {
            "name": setting.name,
            "required": setting.required,
            "description": setting.description,
            "service_type": service_type,
            "setting_type": get_setting_type_from_setting(setting),
            "options": get_service_options(service_type)
        }
        services.append(newSetting)

    get_data_json = {
        "data": services,
        "returnMethod": "configureServices",
        "jsHelperFunction": "processServices",
        "app_py_path": app_py_path,
        "current_app_name": app_instance.package
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )


async def configureServices(services_data, channel_layer):
    try:
        link_service_to_app_setting(services_data['service_type'],
                                    services_data['service_id'],
                                    services_data['app_name'],
                                    services_data['setting_type'],
                                    services_data['service_name'])
    except Exception as e:
        print(e)
        print("Error while linking service")
        return

    get_data_json = {
        "data": {"serviceName": services_data['service_name']},
        "jsHelperFunction": "serviceConfigComplete"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )


async def getServiceList(data, channel_layer):
    get_data_json = {
        "data": {"settingType": data['settingType'],
                 "newOptions": get_service_options(data['settingType'])},
        "jsHelperFunction": "updateServiceListing"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )
