import os
import git
import threading
import time
import logging
import uuid
import json

from tethys_cli.install_commands import (open_file, validate_schema)
from tethys_sdk.routing import controller
from tethys_sdk.workspaces import get_app_workspace
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.core.cache import cache
from pathlib import Path
from subprocess import (Popen, PIPE, STDOUT)
from datetime import datetime

from .app import AppStore as app
from .helpers import Commands, conda_run, get_override_key, logger
from .installation_handlers import restart_server

FNULL = open(os.devnull, 'w')
CACHE_KEY = "warehouse_github_app_resources"

git_install_logger = logging.getLogger("warehouse_git_install_logger")
git_install_logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s : %(message)s')


def clear_github_cache_list():
    # This method clears out the stored cache of GitHub installed apps.
    cache.delete(CACHE_KEY)


def run_pending_installs():
    # This function is run when this module gets loaded at reboots
    # Picks up on any pending installs based on the status files
    # Sleep for 10 s. This could just be a restart attempt and in case it is, we don't want to continue until
    # it's completely done and the server is ready.
    time.sleep(10)
    logger.info("Checking for Pending Installs")

    app_workspace = get_app_workspace(app)
    workspace_directory = app_workspace.path

    install_status_dir = os.path.join(
        workspace_directory, 'install_status', 'github')
    if not os.path.exists(install_status_dir):
        return
    # Check each file for any that are still not completed or errored out
    for file_name in os.listdir(install_status_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(install_status_dir, file_name)
            with open(os.path.join(install_status_dir, file_name), "r") as json_file:
                data = json.load(json_file)
                # Check if setupPy is running and continue the install for that
                if data["status"]["setupPy"] == "Running":
                    logger.info("Continuing Install for " + data["installID"])
                    # Create logging handler
                    workspace_directory = app_workspace.path
                    install_logs_dir = os.path.join(
                        workspace_directory, 'logs', 'github_install')
                    logfile_location = os.path.join(
                        install_logs_dir, data["installID"] + '.log')
                    fh = logging.FileHandler(logfile_location)
                    fh.setFormatter(logger_formatter)
                    fh.setLevel(logging.DEBUG)
                    git_install_logger.addHandler(fh)

                    install_yml_path = Path(os.path.join(
                        data["workspacePath"], 'install.yml'))
                    install_options = open_file(install_yml_path)
                    if "name" in install_options:
                        app_name = install_options['name']

                    continue_install(git_install_logger,
                                     file_path, install_options, app_name, app_workspace)


def update_status_file(path, status, status_key, error_msg=""):

    with open(path, "r") as json_file:
        data = json.load(json_file)

    data["status"][status_key] = status

    # Check if all status is set to true
    if all(value is True for value in data["status"].values()):
        # Install is completed
        data["installCompletedTime"] = datetime.now().strftime(
            '%Y-%m-%dT%H:%M:%S.%f')
        data["installComplete"] = True

    if error_msg != "":
        data["errorDateTime"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        data["errorMessage"] = error_msg
    else:
        data["lastUpdate"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

    with open(path, "w") as json_file:
        json.dump(data, json_file)


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
            update_status_file(status_file_path, False, "conda", error_msg)
        else:
            update_status_file(status_file_path, True, "conda")
            logger.info(resp)


def write_logs(logger, output, subHeading):
    with output:
        for line in iter(output.readline, b''):
            cleaned_line = line.decode("utf-8").replace("\n", "")
            logger.info(subHeading + cleaned_line)


def continue_install(logger, status_file_path, install_options, app_name, app_workspace):
    process = Popen(['tethys', 'db', 'sync'], stdout=PIPE, stderr=STDOUT)
    write_logs(logger, process.stdout, 'Tethys DB Sync : ')
    exitcode = process.wait()
    if exitcode == 0:
        update_status_file(status_file_path, True, "dbSync")
    else:
        update_status_file(status_file_path, False, "dbSync",
                           "Error while running DBSync. Please check logs")

    # Check to see if any extra scripts need to be run
    if validate_schema('post', install_options):
        logger.info("Running post installation tasks...")
        for post in install_options["post"]:
            # TODO: Verify that this works
            path_to_post = status_file_path.resolve().parent / post
            # Attempting to run processes.
            process = Popen(str(path_to_post), shell=True, stdout=PIPE)
            stdout = process.communicate()[0]
            logger.info("Post Script Result: {}".format(stdout))

    update_status_file(status_file_path, True, "post")
    update_status_file(status_file_path, True, "setupPy")
    logger.info("Install completed")
    clear_github_cache_list()
    restart_server({"restart_type": "github_install", "name": app_name}, channel_layer=None, app_workspace=app_workspace)


def install_worker(workspace_apps_path, status_file_path, logger, install_run_id, develop, app_workspace):
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
                process = Popen(
                    ['pip', 'install', *requirements_config["pip"]], stdout=PIPE, stderr=STDOUT)
                write_logs(logger, process.stdout, 'PIP Install: ')
                exitcode = process.wait()
                logger.info("PIP Install exited with: " + str(exitcode))

    update_status_file(status_file_path, True, "conda")
    update_status_file(status_file_path, True, "pip")
    update_status_file(status_file_path, "Running", "setupPy")

    # Run Setup.py
    logger.info("Running application install....")
    command = "install"
    if develop:
        command = "develop"
    process = Popen(['python', 'setup.py', command],
                    cwd=workspace_apps_path, stdout=PIPE, stderr=STDOUT)
    write_logs(logger, process.stdout, 'Python Install SubProcess: ')
    exitcode = process.wait()
    logger.info("Python Application install exited with: " + str(exitcode))

    # This step might cause a server restart and will not have the rest of the code execute.
    continue_install(logger, status_file_path, install_options, app_name, app_workspace)


def get_log_file(id, app_workspace):
    # Find LogFile
    workspace_directory = app_workspace.path
    install_logs_dir = os.path.join(
        workspace_directory, 'logs', 'github_install')
    os.path.join(install_logs_dir, id + '.log')


def get_status_main(request, app_workspace):
    install_id = request.GET.get('install_id')
    if install_id is None:
        raise ValidationError({"install_id": "Missing Value"})

    # Find the file in the
    status_file_path = os.path.join(
        app_workspace.path, 'install_status', 'github', install_id + '.json')
    if os.path.exists(status_file_path):
        with open(status_file_path, "r") as jsonFile:
            data = json.load(jsonFile)
        return JsonResponse(data)
    else:
        raise Http404("No Install with id: " + install_id + " exists")


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@controller(
    name='git_get_status',
    url='app-store/install/git/status',
    app_workspace=True,
)
def get_status(request, app_workspace):
    # This method is a wrapper function to protect the actual method from being accessed without auth
    get_status_main(request, app_workspace)


@api_view(['GET'])
@csrf_exempt
@controller(
    name='git_get_status_override',
    url='app-store/install/git/status_override',
)
def get_status_override(request):
    # This method is an override to the get status method. It allows for installation
    # based on a custom key set in the custom settings.
    # This allows app nursery to use the same code to process the request
    override_key = get_override_key()
    if(request.GET.get('custom_key') == override_key):
        return get_status_main(request)
    else:
        return HttpResponse('Unauthorized', status=401)


def get_logs_main(request, app_workspace):
    install_id = request.GET.get('install_id')
    if install_id is None:
        raise ValidationError({"install_id": "Missing Value"})

    # Find the file in the
    file_path = os.path.join(app_workspace.path, 'logs',
                             'github_install', install_id + '.log')
    if os.path.exists(file_path):
        with open(file_path, "r") as logFile:
            return HttpResponse(logFile, content_type='text/plain')
    else:
        raise Http404("No Install with id: " + install_id + " exists")


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@controller(
    name='git_get_logs',
    url='app-store/install/git/logs',
    app_workspace=True,
)
def get_logs(request, app_workspace):
    get_logs_main(request, app_workspace)


@api_view(['GET'])
@csrf_exempt
@controller(
    name='git_get_logs_override',
    url='app-store/install/git/logs_override',
)
def get_logs_override(request):
    # This method is an override to the get status method. It allows for installation
    # based on a custom key set in the custom settings.
    # This allows app nursery to use the same code to process the request
    override_key = get_override_key()
    if(request.GET.get('custom_key') == override_key):
        return get_logs_main(request)
    else:
        return HttpResponse('Unauthorized', status=401)


@controller(
    name='install_git',
    url='app-store/install/git',
    app_workspace=True,
)
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def run_git_install_main(request, app_workspace):
    workspace_directory = app_workspace.path
    install_logs_dir = os.path.join(
        workspace_directory, 'logs', 'github_install')
    install_status_dir = os.path.join(
        workspace_directory, 'install_status', 'github')

    # Set InstallRunning File in workspace directory
    # This file prevents the file-watcher from restarting the container in case this is running in the App Nursery

    if not os.path.exists(install_status_dir):
        os.makedirs(install_status_dir)

    Path(os.path.join(workspace_directory, 'install_status', 'installRunning')).touch()

    received_json_data = json.loads(request.body)
    if 'url' in received_json_data:
        repo_url = received_json_data.get('url', '')
        branch = received_json_data.get('branch', 'master')
    else:
        # Try formData
        repo_url = request.POST.get('url', '')
        branch = request.POST.get('branch', 'master')

    develop = "false"
    if 'develop' in received_json_data:
        develop = received_json_data.get('develop', False)

    url_end = repo_url.split("/")[-1]
    url_end = url_end.replace(".git", "")

    if not os.path.exists(install_logs_dir):
        os.makedirs(install_logs_dir)

    install_run_id = str(uuid.uuid4())

    # Create new logFile
    logfile_location = os.path.join(install_logs_dir, install_run_id + '.log')
    fh = logging.FileHandler(logfile_location)
    fh.setFormatter(logger_formatter)
    fh.setLevel(logging.DEBUG)

    # TODO: Validation on the GitHUB URL
    workspace_apps_path = os.path.join(
        workspace_directory, 'apps', 'github_installed', url_end)

    # Create new statusFile

    statusfile_location = os.path.join(
        install_status_dir, install_run_id + '.json')
    statusfile_data = {
        'installID': install_run_id,
        'githubURL': repo_url,
        'workspacePath': workspace_apps_path,
        'installComplete': False,
        'status': {
            "installStarted": True,
            "conda": "Pending",
            "pip": "Pending",
            "setupPy": "Pending",
            "dbSync": "Pending",
            "post": "Pending"
        },
        'installStartTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    }
    with open(statusfile_location, 'w') as outfile:
        json.dump(statusfile_data, outfile)

    git_install_logger.addHandler(fh)
    git_install_logger.info(
        "Starting GitHub Install. Installation ID: " + install_run_id)
    git_install_logger.info("Input URL: " + repo_url)
    git_install_logger.info("Assumed App Name: " + url_end)

    git_install_logger.info("Application Install Path: " + workspace_apps_path)

    # Create Dir if it doesn't exist
    if not os.path.exists(workspace_apps_path):
        git_install_logger.info(
            "App folder Directory does not exist. Creating one.")
        os.makedirs(workspace_apps_path)
        # Clone Directory into this path
        repo = git.Repo.init(workspace_apps_path)
        origin = repo.create_remote('origin', repo_url)
        origin.fetch()

        # Git has changed the default branch name to main so this next command might fail with git.exc.GitCommandError
        try:
            repo.git.checkout(branch, "-f")
        except git.exc.GitCommandError:
            git_install_logger.info(
                "Couldn't check out " + branch + " branch. Attempting to checkout main")
            repo.git.checkout("main", "-f")
    else:
        # The Dir Exists. This app is possibly already installed.
        # Do A Pull and Continue
        git_install_logger.info("Git Repo exists locally. Doing a pull to get the latest")
        g = git.cmd.Git(workspace_apps_path)
        g.pull()

    # Run command in new thread
    install_thread = threading.Thread(target=install_worker, name="InstallApps",
                                      args=(workspace_apps_path, statusfile_location, git_install_logger,
                                            install_run_id, develop, app_workspace))
    # install_thread.setDaemon(True)
    install_thread.start()

    return JsonResponse({'status': "InstallRunning", 'install_id': install_run_id})


@api_view(['POST'])
@permission_classes([AllowAny])
@controller(
    name='install_git_override',
    url='app-store/install/git_override',
    login_required=False
)
@csrf_exempt
@controller(
    name='install_git_override',
    url='app-store/install/git_override',
)
def run_git_install_override(request):
    # This method is an override to the install method. It allows for installation
    # based on a custom key set in the custom settings. This allows app nursery to use the same code to process the
    # request
    override_key = get_override_key()
    if(request.GET.get('custom_key') == override_key):
        return run_git_install_main(request)
    else:
        return HttpResponse('Unauthorized', status=401)


resume_thread = threading.Thread(
    target=run_pending_installs, name="ResumeGitInstalls")
resume_thread.setDaemon(True)
resume_thread.start()
