import shutil
import yaml
import os
import git

from subprocess import (call, Popen, PIPE, STDOUT)
from argparse import Namespace
from conda.cli.python_api import run_command as conda_run, Commands
from django.core.exceptions import ObjectDoesNotExist
from tethys_apps.cli.cli_colors import pretty_output, FG_RED, FG_BLUE, FG_YELLOW

from tethys_apps.cli.services_commands import (services_create_persistent_command, services_create_spatial_command,
                                               services_create_dataset_command, services_create_wps_command,
                                               services_list_command)


from tethys_apps.cli.syncstores_command import syncstores_command


from tethys_apps.utilities import link_service_to_app_setting

FNULL = open(os.devnull, 'w')

serviceLinkParam = {
    'spatial': 'ds_spatial',
    "dataset": 'ds_dataset',
    "persistent": 'ps_database',
    'wps': 'wps'
}

tethysapp_dir = os.path.dirname(os.path.dirname(__file__))
root_app_path = os.path.join(tethysapp_dir, 'tethysapp')
thredds_dir = os.path.join(os.path.dirname(tethysapp_dir), 'thredds', 'public')


def write_error(msg):
    with pretty_output(FG_RED) as p:
        p.write(msg)
    exit(1)


def write_msg(msg):
    with pretty_output(FG_YELLOW) as p:
        p.write(msg)


def create_services(service, create_service, config):
    newService = None

    try:
        newService = service.objects.get(name=config['name'])
        write_msg('Service with name "{0}" already exists. Skipping add.'.format(config['name']))
    except ObjectDoesNotExist:
        if not service:
            write_error('Invalid Service Type : {0}.'.format(serviceKey))

        serviceMethod = create_service
        tempNS = Namespace()

        for conf in config.keys():
            setattr(tempNS, conf, config[conf])

        newService = serviceMethod(tempNS)


def get_service_from_id(id):

    from tethys_services.models import (SpatialDatasetService, PersistentStoreService,
                                        DatasetService, WebProcessingService)

    try:
        persistent_entries = PersistentStoreService.objects.get(id=id)  # noqa: F841
        return {"service_type": "persistent",
                "linkParam": serviceLinkParam['persistent']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = SpatialDatasetService.objects.get(id=id)  # noqa: F841
        return {"service_type": "spatial",
                "linkParam": serviceLinkParam['spatial']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = DatasetService.objects.get(id=id)  # noqa: F841
        return {"service_type": "dataset",
                "linkParam": serviceLinkParam['dataset']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = WebProcessingService.objects.get(id=id)  # noqa: F841
        return {"service_type": "wps",
                "linkParam": serviceLinkParam['persistent']}
    except ObjectDoesNotExist:
        pass

    return False


def get_service_from_name(name):

    from tethys_services.models import (SpatialDatasetService, PersistentStoreService,
                                        DatasetService, WebProcessingService)

    try:
        persistent_entries = PersistentStoreService.objects.get(name=name)  # noqa: F841
        return {"service_type": "persistent",
                "linkParam": serviceLinkParam['persistent']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = SpatialDatasetService.objects.get(name=name)  # noqa: F841
        return {"service_type": "spatial",
                "linkParam": serviceLinkParam['spatial']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = DatasetService.objects.get(name=name)  # noqa: F841
        return {"service_type": "dataset",
                "linkParam": serviceLinkParam['dataset']}
    except ObjectDoesNotExist:
        pass

    try:
        entries = WebProcessingService.objects.get(name=name)  # noqa: F841
        return {"service_type": "wps",
                "linkParam": serviceLinkParam['wps']}
    except ObjectDoesNotExist:
        pass

    return False


# Pulling this function out so I can mock this for inputs to the interactive mode

def get_interactive_input():
    return input("")


def get_service_name_input():
    return input("")


def parse_id_input(inputResponse):
    id_search = False

    try:
        ids = inputResponse.split(',')
        ids = list(map(lambda x: int(x), ids))

        id_search = True
    except ValueError:
        ids = [inputResponse]
        pass

    return id_search, ids


def run_interactive_services(app_name):
    write_msg('Running Interactive Service Mode. '
              'Any configuration options in install.yml for services will be ignored...')

    # List existing services
    tempNS = Namespace()

    for conf in ['spatial', 'persistent', 'wps', 'dataset']:
        setattr(tempNS, conf, False)

    services_list_command(tempNS)

    write_msg('Please enter the service ID/Name to link one of the above listed service.')
    write_msg('You may also enter a comma seperated list of service ids : (1,2).')
    write_msg('Just hit return if you wish to skip this step and move on to creating your own services.')

    valid = False
    while not valid:
        try:
            response = get_interactive_input()
            if response != "":
                # Parse Response
                id_search, ids = parse_id_input(response)

                for service_id in ids:
                    if id_search:
                        service = get_service_from_id(service_id)
                    else:
                        service = get_service_from_name(service_id)
                    if service:
                        # Ask for app setting name:
                        write_msg(
                            'Please enter the name of the service from your app.py eg: "catalog_db")')
                        setting_name = get_service_name_input()
                        link_service_to_app_setting(service['service_type'],
                                                    service_id,
                                                    app_name,
                                                    service['linkParam'],
                                                    setting_name)

                valid = True

            else:
                write_msg(
                    "Please run 'tethys services create -h' to create services via the command line.")
                valid = True

        except (KeyboardInterrupt, SystemExit):
            with pretty_output(FG_YELLOW) as p:
                p.write('\nInstall Command cancelled.')
            exit(0)


def find_and_link(service_type, setting_name, service_id, app_name):

    service = get_service_from_name(service_id)
    if service:
        link_service_to_app_setting(service['service_type'],
                                    service_id,
                                    app_name,
                                    service['linkParam'],
                                    setting_name)
    else:
        with pretty_output(FG_RED) as p:
            p.write(
                'Warning: Could not find service of type: {} with the name/id: {}'.format(service_type, service_id))


def run_portal_init(service_models, file_path, app_name):

    if file_path is None:
        file_path = './portal.yml'

    if not os.path.exists(file_path):
        write_msg("No Portal Services file found. Moving to look for local app level services.yml...")
        return False

    try:
        write_msg("Portal init file found...Processing...")
        with open(file_path) as f:
            portal_options = yaml.safe_load(f)

    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write('An unexpected error occurred reading the file. Please try again.')
            return False

    if "apps" in portal_options and app_name in portal_options['apps'] and 'services' in portal_options['apps'][app_name]:
        services = portal_options['apps'][app_name]['services']
        if services and len(services) > 0:
            for service_type in services:
                if services[service_type] is not None:
                    current_services = services[service_type]
                    for service_setting_name in current_services:
                        find_and_link(service_type, service_setting_name,
                                      current_services[service_setting_name], app_name)
        else:
            write_msg("No app configuration found for app: {} in portal config file. ".format(app_name))

    else:
        write_msg("No apps configuration found in portal config file. ".format(app_name))

    return True


def install_dependencies(conda_config, pip_config):
    # Add all channels listed in the file.
    if "channels" in conda_config and conda_config['channels'] and len(conda_config['channels']) > 0:
        channels = conda_config['channels']
        for channel in channels:
            [resp, err, code] = conda_run(
                Commands.CONFIG, "--prepend", "channels", channel, use_exception_handler=False)

    # Install all Dependencies

    if "dependencies" in conda_config and conda_config['dependencies'] and len(conda_config['dependencies']) > 0:
        dependencies = conda_config['dependencies']
        with pretty_output(FG_BLUE) as p:
            p.write('Installing Dependencies.....')
        [resp, err, code] = conda_run(
            Commands.INSTALL, *dependencies, use_exception_handler=False, stdout=None, stderr=None)
        if code != 0:
            with pretty_output(FG_RED) as p:
                p.write('Warning: Dependencies installation ran into an error. Please try again or a manual install')

    if pip_config and len(pip_config) > 0:
        for pip_req in pip_config:
            from pip._internal import main as pip
            pip(['install', '--user', pip_req])


def run_services(services_config, file_path, app_name, serviceFileInput):

    if serviceFileInput is None:
        file_path = './services.yml'
    else:
        file_path = serviceFileInput

    if not os.path.exists(file_path):
        write_msg("No Services init file found. Skipping app service installation")
        return

    try:
        with open(file_path) as f:
            init_options = yaml.safe_load(f)

    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write('An unexpected error occurred reading the file. Please try again.')
            exit(1)

    # Setup any services that need to be setup
    services = init_options
    interactive_mode = False
    skip = False

    if "skip" in services:
        skip = services['skip']
        del services['skip']
    if "interactive" in services:
        interactive_mode = services['interactive']
        del services['interactive']

    if not skip:
        if interactive_mode:
            run_interactive_services(app_name)
        else:
            if services and len(services) > 0:
                if 'version' in services:
                    del services['version']
                for service_type in services:
                    if services[service_type] is not None:
                        current_services = services[service_type]
                        for service_setting_name in current_services:
                            find_and_link(service_type, service_setting_name,
                                          current_services[service_setting_name], app_name)
        write_msg("Services Configuration Completed.")
    else:
        write_msg("Skipping services configuration, Skip option found.")


def process_production_services(service_options, service_models):

    creators = {
        'spatial': services_create_spatial_command,
        "dataset": services_create_dataset_command,
        "persistent": services_create_persistent_command,
        'wps': services_create_wps_command
    }

    for service_type in service_options:
        if service_options[service_type]:
            for service in service_options[service_type]:
                create_services(service_models[service_type], creators[service_type], service)


def process_production_apps(apps):

    for app_name in apps:
        if "source" in apps[app_name]:
            write_msg("Pulling application from source....")
            dir_path = os.path.join(root_app_path, app_name)
            service_file_path = os.path.join(dir_path, 'services.yml')
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)

            os.mkdir(dir_path)

            repo = git.Repo.init(dir_path)
            origin = repo.create_remote('origin', apps[app_name]["source"]["url"])
            origin.fetch()
            branch = "master"
            if "branch" in apps[app_name]["source"]:
                branch = apps[app_name]["source"]["branch"]

            repo.git.checkout(branch)

            for root, dirs, files in os.walk(dir_path):
                for momo in dirs:
                    os.chmod(os.path.join(root, momo), 0o755)
                for momo in files:
                    os.chmod(os.path.join(root, momo), 0o755)

            if "services" in apps[app_name]:
                with open(service_file_path, 'w') as outfile:
                    yaml.dump(apps[app_name]["services"], outfile)
            else:
                if os.path.isfile(service_file_path):
                    os.remove(service_file_path)

            # Run the app install command with new params
            tempNS = Namespace()

            setattr(tempNS, 'file', os.path.join(dir_path, 'install.yml'))
            setattr(tempNS, 'services_file', service_file_path)
            setattr(tempNS, 'portal_file', None)
            setattr(tempNS, 'exit', False)

            init_command(tempNS)

            if "custom_settings" in apps[app_name]:
                process_custom_settings(apps[app_name]['custom_settings'], app_name)

        else:
            write_error("No App source present for App: {}. Aborting.".format(app_name))


def process_custom_settings(settings, app_name):
    write_msg("Processing Custom Settings for app {}".format(app_name))

    try:
        # Try to get the app
        from tethys_apps.models import TethysApp
        db_app = TethysApp.objects.get(package=app_name)

        if db_app is None:
            write_msg("Cannot configure custom settings. Check errors...")

        custom_settings = db_app.custom_settings
        for setting_name in settings:
            try:
                custom_setting = custom_settings.get(name=setting_name)
                value = settings[setting_name]
                if value == "thredds_dir":
                    value = os.path.join(thredds_dir, app_name)
                custom_setting.set_value(value)
                custom_setting.save()
            except ObjectDoesNotExist:
                write_msg("Custom setting doesn't exist : {}".format(setting_name))

    except Exception as e:
        print(e)


def process_portal_settings(settings):
    write_msg("Processing Portal Settings")

    try:
        # Try to get the settings
        from tethys_config.models import Setting

        for new_setting in settings:
            portal_setting_obj = Setting.objects.get(name=new_setting)
            setattr(portal_setting_obj, 'content', settings[new_setting])
            portal_setting_obj.save()

    except Exception as e:
        print(e)


def run_production_install(file_path, service_models):

    if file_path is None:
        return

    if not os.path.exists(file_path):
        write_error("No Production File found at that path. Aborting. ")

    try:
        with open(file_path) as f:
            production_options = yaml.safe_load(f)

    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write(
                'An unexpected error occurred reading the file. Please try again.')
            exit(1)

    if "services" in production_options:
        process_production_services(production_options['services'], service_models)

    if "apps" in production_options:
        process_production_apps(production_options['apps'])

    if "portal_settings" in production_options:
        process_portal_settings(production_options['portal_settings'])

    write_msg("Syncing database for all installed applications...")

    # Run the app install command with new params
    tempNS = Namespace()

    setattr(tempNS, 'app', ['all'])
    setattr(tempNS, 'refresh', None)
    setattr(tempNS, 'firsttime', None)
    setattr(tempNS, 'database', None)

    syncstores_command(tempNS)

    exit(0)


def init_command(args):
    """
    Init Command
    """

    # Have to import within function or else install partial on a system fails
    from tethys_services.models import (
        SpatialDatasetService, DatasetService, PersistentStoreService, WebProcessingService)

    service_models = {
        'spatial': SpatialDatasetService,
        "dataset": DatasetService,
        "persistent": PersistentStoreService,
        'wps': WebProcessingService
    }

    app_name = None
    if 'production_file' in args:
        run_production_install(args.production_file, service_models)

    # Check if input config file exists. We Can't do anything without it
    if 'file' in args:
        file_path = args.file

    if file_path is None:
        file_path = './install.yml'

    if not os.path.exists(file_path):
        write_error(
            'No Install File found. Please ensure install.yml exists or check the file path entered.')

    try:
        with open(file_path) as f:
            init_options = yaml.safe_load(f)

    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write(
                'An unexpected error occurred reading the file. Please try again.')
            exit(1)

    call_cwd_path = os.path.dirname(file_path)

    if "name" in init_options:
        app_name = init_options['name']

    if "conda" not in init_options:
        with pretty_output(FG_BLUE) as p:
            p.write(
                'No Conda options found. Does your app not have any dependencies?')
        exit(0)

    conda_config = init_options['conda']
    if 'pip' in init_options:
        pip_config = init_options['pip']
    else:
        pip_config = None

    skip = False
    if "skip" in conda_config:
        skip = conda_config['skip']
        del conda_config['skip']

    if skip:
        write_msg("Skipping dependency installation, Skip option found.")
    else:
        pass
        install_dependencies(conda_config, pip_config)

    # Run Setup.py
    write_msg("Running application install....")

    if 'setup_path' in init_options:
        setup_path = init_options['setup_path']
    else:
        setup_path = "setup.py"

    call(['python', setup_path, 'develop'], cwd=call_cwd_path, stderr=STDOUT)

    call(['tethys', 'manage', 'sync'])

    service_file_path = None
    if 'services_file' in args:
        service_file_path = args.services_file
    # Run Portal Level Config if present
    if 'force_services' in args:
        if args.force_services:
            run_services(service_models, file_path, app_name, service_file_path)
    else:
        portal_result = run_portal_init(service_models, args.portal_file, app_name)
        if not portal_result:
            run_services(service_models, file_path, app_name, service_file_path)

    # Check to see if any extra scripts need to be run

    if "post" in init_options and init_options["post"] and len(init_options["post"]) > 0:
        write_msg("Running post installation tasks...")
        source_dir = os.path.dirname(tethysapp_dir)
        for post in init_options["post"]:
            path_to_post = os.path.join(os.path.dirname(os.path.realpath(file_path)), post)
            # Attempting to run processes.
            process = Popen(['bash', path_to_post, source_dir], stdout=PIPE)
            stdout = process.communicate()[0]
            write_msg("Post Script Result: {}".format(stdout))

    if "exit" in args:
        if args.exit:
            exit(0)
        else:
            return
    else:
        exit(0)
