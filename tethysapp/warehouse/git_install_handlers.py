import os
import git
import threading
import time

from tethys_cli.install_commands import (install_command, open_file, validate_schema, install_packages)
from tethys_sdk.workspaces import app_workspace

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.http import JsonResponse
from django.core.cache import cache
from argparse import Namespace
from pathlib import Path
from subprocess import (call, Popen, PIPE, STDOUT)


from .app import Warehouse as app
from .helpers import *
from .installation_handlers import restart_server

FNULL = open(os.devnull, 'w')


def install_worker(workspace_apps_path):
    # Install Dependencies
    logger.info("Installing dependencies...")
    file_path = Path(os.path.join(workspace_apps_path, 'install.yml'))
    install_options = open_file(file_path)

    if "name" in install_options:
        app_name = install_options['name']

    if validate_schema('requirements', install_options):
        requirements_config = install_options['requirements']
        skip = False
        if "skip" in requirements_config:
            skip = requirements_config['skip']

        if skip:
            logger.info("Skipping package installation, Skip option found.")
        else:
            if validate_schema('conda', requirements_config):  # noqa: E501
                conda_config = requirements_config['conda']
                install_packages(conda_config, update_installed=False)
            if validate_schema('pip', requirements_config):
                logger.info("Running pip installation tasks...")
                call(['pip', 'install', *requirements_config["pip"]])

    # Run Setup.py
    logger.info("Running application install....")
    Popen(['python', 'setup.py', 'install'], cwd=workspace_apps_path)
    call(['tethys', 'db', 'sync'])

    # Check to see if any extra scripts need to be run
    if validate_schema('post', install_options):
        logger.info("Running post installation tasks...")
        for post in install_options["post"]:
            path_to_post = file_path.resolve().parent / post
            # Attempting to run processes.
            process = Popen(str(path_to_post), shell=True, stdout=PIPE)
            stdout = process.communicate()[0]
            logger.info("Post Script Result: {}".format(stdout))

    restart_server({"restart_type": "gInstall", "name": app_name}, None)


@ api_view(['POST'])
@ authentication_classes((TokenAuthentication,))
def run_git_install(request):
    repo_url = request.POST.get('url', '')
    url_end = repo_url.split("/")[-1]
    url_end = url_end.replace(".git", "")

    # Get workspace since @app_workspace doesn't work with api request?
    project_directory = os.path.dirname(sys.modules[app.__module__].__file__)
    workspace_directory = os.path.join(project_directory, 'workspaces', 'app_workspace')

    # TODO: Validation on the GitHUB URL
    workspace_apps_path = os.path.join(workspace_directory, 'apps', 'installed', url_end)

    # Create Dir if it doesn't exist
    if not os.path.exists(workspace_apps_path):
        os.makedirs(workspace_apps_path)
        # Clone Directory into this path
        print(workspace_apps_path)
        repo = git.Repo.init(workspace_apps_path)
        origin = repo.create_remote('origin', repo_url)
        origin.fetch()

        # Git has changed the default branch name to main so this next command might fail with git.exc.GitCommandError
        try:
            repo.git.checkout("master", "-f")
        except git.exc.GitCommandError:
            logger.info("Couldn't check out master branch. Attempting to checkout main")
            repo.git.checkout("main", "-f")

    # Run command in new thread
    install_thread = threading.Thread(target=install_worker, name="InstallApps",
                                      args=(workspace_apps_path,))
    install_thread.start()

    return JsonResponse({})
