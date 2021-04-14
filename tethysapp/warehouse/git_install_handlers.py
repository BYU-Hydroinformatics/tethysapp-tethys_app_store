import os
import git
import threading
import time
import logging
import uuid
import json

from tethys_cli.install_commands import (install_command, open_file, validate_schema)
from tethys_sdk.workspaces import app_workspace

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import ValidationError, ParseError

from django.http import JsonResponse, Http404, HttpResponse

from django.core.cache import cache
from argparse import Namespace
from pathlib import Path
from subprocess import (call, Popen, PIPE, STDOUT)
from datetime import datetime

from .app import Warehouse as app
from .helpers import *
from .installation_handlers import restart_server

FNULL = open(os.devnull, 'w')


git_install_logger = logging.getLogger("warehouse_git_install_logger")
git_install_logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s : %(message)s')


# This function is run when this module gets loaded at reboots
# Picks up on any pending installs based on the status files
def run_pending_installs():
    app_workspace = app.get_app_workspace()
    workspace_directory = app_workspace.path
    install_status_dir = os.path.join(workspace_directory, 'install_status', 'github')
    # Check each file for any that are still not completed or errored out
    for filename in os.listdir(install_status_dir):
        if filename.endswith(".json"):
            with open(os.path.join(install_status_dir, filename), "r") as jsonFile:
                data = json.load(jsonFile)
                print(data)


def update_status_file(path, status, error_msg=""):
    if status == "Completed":
        with open(path, "r") as jsonFile:
            data = json.load(jsonFile)

        data["status"] = "Complete"
        data["completionDateTime"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        print(data)
        with open(path, "w") as jsonFile:
            json.dump(data, jsonFile)

    if status == "Error":
        with open(path, "r") as jsonFile:
            data = json.load(jsonFile)

        data["status"] = "Error"
        data["errorDateTime"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        data["errorMessage"] = error_msg

        with open(path, "w") as jsonFile:
            json.dump(data, jsonFile)


def install_packages(conda_config, logger, status_file_path):
    # Compile channels arguments
    install_args = []
    if validate_schema('channels', conda_config):
        channels = conda_config['channels']
        for channel in channels:
            install_args.extend(['-c', channel])

    # Install all Packages
    if validate_schema('packages', conda_config):
        install_args.extend(['--freeze-installed'])
        install_args.extend(conda_config['packages'])
        logger.info("Running conda installation tasks...")
        [resp, err, code] = conda_run(Commands.INSTALL, *install_args, use_exception_handler=False)
        if code != 0:
            error_msg = 'Warning: Packages installation ran into an error. Please try again or a manual install'
            logger.error(error_msg)
            update_status_file(status_file_path, "Error", error_msg)
        else:
            logger.info(resp)


def write_logs(logger, output, subHeading):
    with output:
        for line in iter(output.readline, b''):
            cleaned_line = line.decode("utf-8").replace("\n", "")
            logger.info(subHeading + cleaned_line)


def install_worker(workspace_apps_path, status_file_path, logger):
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
                install_packages(conda_config, logger, status_file_path)
            if validate_schema('pip', requirements_config):
                logger.info("Running pip installation tasks...")
                process = Popen(['pip', 'install', *requirements_config["pip"]], stdout=PIPE, stderr=STDOUT)
                write_logs(logger, process.stdout, 'PIP Install: ')
                exitcode = process.wait()
                logger.info("PIP Install exited with: " + str(exitcode))

    # Run Setup.py
    # logger.info("Running application install....")
    # process = Popen(['python', 'setup.py', 'install'], cwd=workspace_apps_path, stdout=PIPE, stderr=STDOUT)
    # write_logs(logger, process.stdout, 'Python Install SubProcess: ')
    # exitcode = process.wait()
    # logger.info("Python Application install exited with: " + str(exitcode))

    process = Popen(['tethys', 'db', 'sync'], stdout=PIPE, stderr=STDOUT)
    write_logs(logger, process.stdout, 'Tethys DB Sync : ')
    exitcode = process.wait()

    # Check to see if any extra scripts need to be run
    if validate_schema('post', install_options):
        logger.info("Running post installation tasks...")
        for post in install_options["post"]:
            path_to_post = file_path.resolve().parent / post
            # Attempting to run processes.
            process = Popen(str(path_to_post), shell=True, stdout=PIPE)
            stdout = process.communicate()[0]
            logger.info("Post Script Result: {}".format(stdout))

    logger.info("Install completed")
    # Update StatusFile
    update_status_file(status_file_path, "Completed")
    restart_server({"restart_type": "gInstall", "name": app_name}, None)


def get_log_file(id):
    # Find LogFile
    app_workspace = app.get_app_workspace()
    workspace_directory = app_workspace.path
    install_logs_dir = os.path.join(workspace_directory, 'logs', 'github_install')
    logfile_location = os.path.join(install_logs_dir, install_run_id + '.log')


@ api_view(['GET'])
@ authentication_classes((TokenAuthentication,))
def get_status(request):

    install_id = request.GET.get('install_id')
    if install_id is None:
        raise ValidationError({"install_id": "Missing Value"})

    # Find the file in the
    app_workspace = app.get_app_workspace()
    status_file_path = os.path.join(app_workspace.path, 'install_status', 'github', install_id + '.json')
    if os.path.exists(status_file_path):
        with open(status_file_path, "r") as jsonFile:
            data = json.load(jsonFile)
        return JsonResponse(data)
    else:
        raise Http404("No Install with id: " + install_id + " exists")


@ api_view(['GET'])
@ authentication_classes((TokenAuthentication,))
def get_logs(request):
    install_id = request.GET.get('install_id')
    if install_id is None:
        raise ValidationError({"install_id": "Missing Value"})

    # Find the file in the
    app_workspace = app.get_app_workspace()
    file_path = os.path.join(app_workspace.path, 'logs', 'github_install', install_id + '.log')
    if os.path.exists(file_path):
        with open(file_path, "r") as logFile:
            return HttpResponse(logFile, content_type='text/plain')
    else:
        raise Http404("No Install with id: " + install_id + " exists")


@ api_view(['POST'])
@ authentication_classes((TokenAuthentication,))
def run_git_install(request):
    repo_url = request.POST.get('url', '')
    url_end = repo_url.split("/")[-1]
    url_end = url_end.replace(".git", "")

    # Check if application is already installed. In that case just pull the

    # Get workspace since @app_workspace doesn't work with api request?
    app_workspace = app.get_app_workspace()
    workspace_directory = app_workspace.path
    install_logs_dir = os.path.join(workspace_directory, 'logs', 'github_install')
    install_status_dir = os.path.join(workspace_directory, 'install_status', 'github')

    if not os.path.exists(install_logs_dir):
        os.makedirs(install_logs_dir)

    if not os.path.exists(install_status_dir):
        os.makedirs(install_status_dir)

    install_run_id = str(uuid.uuid4())
    # Create new logFile
    logfile_location = os.path.join(install_logs_dir, install_run_id + '.log')
    fh = logging.FileHandler(logfile_location)
    fh.setFormatter(logger_formatter)
    fh.setLevel(logging.DEBUG)

    # Create new statusFile
    statusfile_location = os.path.join(install_status_dir, install_run_id + '.json')
    statusfile_data = {
        'githubURL': repo_url,
        'status': "Installation Started",
        'installStartTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    }
    with open(statusfile_location, 'w') as outfile:
        json.dump(statusfile_data, outfile)

    git_install_logger.addHandler(fh)
    git_install_logger.info("Starting GitHub Install. Installation ID: " + install_run_id)
    git_install_logger.info("Input URL: " + repo_url)
    git_install_logger.info("Assumed App Name: " + url_end)

    # TODO: Validation on the GitHUB URL
    workspace_apps_path = os.path.join(workspace_directory, 'apps', 'installed', url_end)
    git_install_logger.info("Application Install Path: " + workspace_apps_path)

    # Create Dir if it doesn't exist
    if not os.path.exists(workspace_apps_path):
        git_install_logger.info("App folder Directory does not exist. Creating one.")
        os.makedirs(workspace_apps_path)
        # Clone Directory into this path
        repo = git.Repo.init(workspace_apps_path)
        origin = repo.create_remote('origin', repo_url)
        origin.fetch()

        # Git has changed the default branch name to main so this next command might fail with git.exc.GitCommandError
        try:
            repo.git.checkout("master", "-f")
        except git.exc.GitCommandError:
            git_install_logger.info("Couldn't check out master branch. Attempting to checkout main")
            repo.git.checkout("main", "-f")

    # Run command in new thread
    install_thread = threading.Thread(target=install_worker, name="InstallApps",
                                      args=(workspace_apps_path, statusfile_location, git_install_logger))
    # install_thread.setDaemon(True)
    install_thread.start()

    return JsonResponse({})


# run_pending_installs()
