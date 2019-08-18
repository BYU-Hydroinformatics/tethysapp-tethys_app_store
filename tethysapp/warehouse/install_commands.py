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

import git
import os
import yaml

from subprocess import call, Popen, PIPE, STDOUT
from conda.cli.python_api import run_command as conda_run, Commands
from .app import Warehouse as app


def handle_property_not_present(property):
    # TODO
    # Generate an error message that metadata is incorrect for this application
    pass


def get_repo(app_name, repo_link, branch="master"):

                # TODO
                # What Happens when git pull fails or one of the other operations in here?

    dir_path = os.path.join(app.get_app_workspace().path, app_name)
    print(dir_path)
    if os.path.isdir(dir_path):
        print("Path already exists, could be an update operation?. Skipping Git checkout, just do a pull")
        repo = git.Repo(dir_path)
        o = repo.remotes.origin
        o.pull()
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


def install_conda_deps(conda_config):
    result = {
        'status': True,
        'msg': ""
    }
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


def run_install(install_path):
    return_msgs = []

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
            conda_install_result = install_conda_deps(conda_config)

    if 'pip' in init_options:
        pip_config = init_options['pip']
        pip_install_result = install_pip_deps(pip_config)
    else:
        pip_install_result = {
            'status': True,
            'msg': "No Pip Dependencies found. Skipped Pip Installation. "
        }

    result_install = conda_install_result['status'] and pip_install_result['status']
    return {
        'status': result_install,
        'msg': 'Install App and Deps Successful',
        'conda_result': conda_install_result,
        'pip_result': pip_install_result
    }


def begin_install(install_metadata):

    app_path = get_repo(install_metadata['metadata']['app-name'], install_metadata['metadata']['github-url'])
    validation = validate_app(app_path)
    install_status = run_install(validation['path'])
    print(install_status)
# print(install_metadata)
