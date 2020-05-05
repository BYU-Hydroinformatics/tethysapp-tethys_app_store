# {'title': 'Warehouse App 1 - Test', 'id': '1604fb12cced4f79bb6ceaf1a2c98090',
#  'description': 'Test Resource for Tethys App Warehouse.',
#  'date_created': '05-20-2019',
#     'date_last_updated': '07-17-2019',
#     'metadata': {'tethys-app': 'true', 'test-metadata': '4443',
#                  'tethys-version': '2.0',
#                  'github-url': 'https://github.com/rfun/warehouse-test.git'}}

# Download github code

# Look for install.yaml

# if none found then show error

# if found, install dependencies, install app

# services check

# custom settings check

import os
import yaml
import time


from subprocess import call, STDOUT
from conda.cli.python_api import run_command as conda_run, Commands
from asgiref.sync import async_to_sync
from pathlib import Path

from .app import Warehouse as app


def send_notification(msg, channel_layer):
    async_to_sync(channel_layer.group_send)(
        "notifications", {
            "type": "install_notifications",
            "message": msg
        }
    )


def process_custom_settings(custom_settings):
    for setting in custom_settings():
        setting.value = "Test Value"
        setting.save()
        print(setting)


def detect_app_dependencies(repo_location):
    """
    Method goes through the app.xml and determines the following:
    1.) Any services required
    2.) Thredds?
    3.) Geoserver Requirement?
    4.) Custom Settings required for installation?
    """
    app_py_possible_files = Path(repo_location).glob('**/app.py')
    app_py_file_location = app_py_possible_files.__next__()

    import importlib.util
    spec = importlib.util.spec_from_file_location("current_app", app_py_file_location)
    current_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current_app)
    current_app = getattr(current_app, 'WarehouseTest')()
    object_methods = [method_name for method_name in dir(current_app)
                      if callable(getattr(current_app, method_name)) and "TethysAppBase" not in str(getattr(current_app, method_name))]

    # Object methods only contains items in the app.py now.

    if 'custom_settings' in object_methods:
        process_custom_settings(getattr(current_app, 'custom_settings'))

    # print(object_methods)

    # print(.__class__.__bases__[0].__name__)
    # print(getattr(current_app, 'custom_settings'))

    # print(object_methods)
    # print(dir(current_app))

    #     print(filename)
    #
    # print(repo_location)
    # app_py_path = os.path.join(app.get_app_workspace().path, 'apps', app_name)

    return


def handle_property_not_present(prop):
    # TODO: Generate an error message that metadata is incorrect for this application
    pass


def get_repo(app_name, repo_link, channel_layer, branch="master", ):
    # TODO :  What Happens when git pull fails or one of the other operations in here?
    send_notification("Pulling GIT Repo", channel_layer)

    dir_path = os.path.join(app.get_app_workspace().path, 'apps', app_name)
    if os.path.isdir(dir_path):
        print("Path already exists, could be an update operation?. Skipping Git checkout, just do a pull")
        # repo = git.Repo(dir_path)
        # o = repo.remotes.origin
        # o.pull()
    else:
        os.mkdir(dir_path)

        repo = git.Repo.init(dir_path)
        origin = repo.create_remote('origin', repo_link)
        origin.fetch()
        repo.git.checkout(branch)

        for root, dirs, files in os.walk(dir_path):
            for momo in dirs:
                os.chmod(os.path.join(root, momo), 0o755)
            for momo in files:
                os.chmod(os.path.join(root, momo), 0o755)

    send_notification("GIT Repo Pull Complete", channel_layer)

    return dir_path


# Function to check if the downloaded repo contains valid install yaml files.

def validate_app(path):
    validation = {'valid': True}
    # Check if Install.yml or install.yaml is present
    install_path = os.path.join(path, 'install')
    if not (os.path.exists(install_path + '.yml') or os.path.exists(install_path + '.yaml')):
        validation['valid'] = False
        return validation
    else:
        if os.path.exists(install_path + '.yml'):
            validation['path'] = install_path + '.yml'
        else:
            validation['path'] = install_path + '.yaml'

    return validation


def conda_install(app_metadata, channel_layer):

    result = {
        'status': True,
        'msg': ""
    }
    send_notification(
        "Conda install may take a couple minutes to complete depending on how complicated the environment is. Please wait....", channel_layer)

    start_time = time.time()
    latest_version = app_metadata['metadata']['versions'][-1]
    app_name = app_metadata['name'] + "=" + latest_version
    run_command = ["-c", app_metadata['metadata']['channel'], app_name, '--json', '--debug']
    [resp, err, code] = conda_run(Commands.INSTALL, *run_command, use_exception_handler=False)
    if code != 0:
        result['status'] = False
        result['msg'] = 'Warning: Dependencies installation ran into an error. Please try again or a manual install'
    else:
        result['msg'] = 'Conda Install Successful'
        send_notification("Conda install completed in %.2f seconds." % (time.time() - start_time), channel_layer)

    return result


def install_conda_deps(conda_config):
    result = {
        'status': True,
        'msg': ""
    }
    install_args = []
    if "channels" in conda_config and conda_config['channels'] and len(conda_config['channels']) > 0:
        channels = conda_config['channels']
    else:
        channels = ['conda-forge']

    # Install all Dependencies

    if "dependencies" in conda_config and conda_config['dependencies'] and len(conda_config['dependencies']) > 0:
        dependencies = conda_config['dependencies']
        print('Installing Conda Dependencies.....')
        run_command = ["-c", *channels, *dependencies]
        [resp, err, code] = conda_run(Commands.INSTALL, *run_command, use_exception_handler=False)
        if code != 0:
            result['status'] = False
            result['msg'] = 'Warning: Dependencies installation ran into an error. Please try again or a manual install'
        else:
            result['msg'] = 'Conda Install Successful'

    return result


def install_pip_deps(pip_config):
    if pip_config and len(pip_config) > 0:
        from pip._internal import main as pip
        for pip_req in pip_config:
            pip(['install', '--user', pip_req])
    return {
        'status': True,
        'msg': "Pip Dependencies Installed"
    }


def run_install(install_path, channel_layer):
    send_notification("Running dependency installation", channel_layer)

    try:
        with open(install_path) as f:
            init_options = yaml.safe_load(f)

    except Exception as e:
        return {
            'status': False,
            'error': e,
            'msg': 'An unexpected error occurred reading the file. Please try again.'
        }

    if "name" in init_options:
        app_name = init_options['name']

    if "conda" not in init_options:
        send_notification("No Conda Dependencies found. Skipped Conda Installation.", channel_layer)

        conda_install_result = {
            'status': True,
            'msg': "No Conda Dependencies found. Skipped Conda Installation. "
        }
    else:
        conda_config = init_options['conda']
        if "skip" in conda_config:
            skip = conda_config['skip']
            conda_install_result = {
                'status': True,
                'msg': "Skipping dependency installation, Skip option found."
            }
        else:
            send_notification("Installing conda dependencies", channel_layer)
            conda_install_result = install_conda_deps(conda_config)
            send_notification("Conda dependecies installation complete", channel_layer)

    if 'pip' in init_options:
        pip_config = init_options['pip']
        send_notification("Installing pip dependencies", channel_layer)
        pip_install_result = install_pip_deps(pip_config)
        send_notification("Pip dependency installation complete", channel_layer)
    else:
        send_notification("No Pip Dependencies found. Skipped Pip Installation.", channel_layer)
        pip_install_result = {
            'status': True,
            'msg': "No Pip Dependencies found. Skipped Pip Installation. "
        }

    result_install = conda_install_result['status'] and pip_install_result['status']
    send_notification("Dependency install complete", channel_layer)
    send_notification("Starting Python application setup (setup.py)", channel_layer)

    if 'setup_path' in init_options:
        setup_path = init_options['setup_path']
    else:
        setup_path = "setup.py"

    call_cwd_path = os.path.dirname(install_path)

    call(['python', setup_path, 'develop'], cwd=call_cwd_path, stderr=STDOUT)
    call(['tethys', 'db', 'sync'])

    send_notification("Python application setup complete", channel_layer)

    return {
        'status': result_install,
        'msg': 'Install App and Deps Successful',
        'conda_result': conda_install_result,
        'pip_result': pip_install_result
    }


def begin_install(install_metadata, channel_layer):
    send_notification("Starting installation of app: " + install_metadata['name'], channel_layer)
    send_notification("Installing latest version", channel_layer)

    try:
        app_path = conda_install(install_metadata, channel_layer)
    except Exception as e:
        print(e)
        send_notification("Error while Installing Conda package. Please check logs for details", channel_layer)
        return

    # try:
    #     app_deps = detect_app_dependencies(app_path)
    # except Exception as e:
    #     print(e)
    #     send_notification("Error while pulling git Repo. Please check logs for details", channel_layer)
    #     return

    # send_notification("Validating downloaded repo", channel_layer)
    #
    # validation = validate_app(app_path)
    #
    # try:
    #     install_status = run_install(validation['path'], channel_layer)
    # except Exception as e:
    #     send_notification("Install ran into an error. Please check logs for details", channel_layer)
    #     return

    # if install_status['status']:
    #     send_notification("install_complete", channel_layer)
