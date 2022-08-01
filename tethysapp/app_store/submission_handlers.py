import git
import os
import shutil
import github
import fileinput
import yaml
import stat
import json
import time
import requests

import requests
from requests.exceptions import HTTPError
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse, HttpResponse
from tethys_sdk.routing import controller

from pathlib import Path

from .app import AppStore as app
from .helpers import logger, send_notification, apply_template, parse_setup_py, get_override_key

key = "#45c0#a820f85aa11d727#f02c382#c91d63be83".replace("#", "e")
g = github.Github(key)

LOCAL_DEBUG_MODE = False


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
@controller(
    name='scaffold_submit',
    url='app-store/scaffold_submit',
    app_workspace=True,
)
def run_submit_nursery_app(request, app_workspace):
    override_key = get_override_key()
    if(request.GET.get('custom_key') == override_key):
        received_json_data = json.loads(request.body)
        return submit_nursery_app(received_json_data.get('app_path'), received_json_data.get('email', ''), app_workspace)
        return HttpResponse('Unauthorized', status=401)


def submit_nursery_app(app_path, requester_email, app_workspace):

    # Ensure there is no slash at the end.
    app_name = app_path.split('/')[-1]

    github_dir = os.path.join(app_workspace.path, 'gitsubmission')

    # create if github Dir does not exist
    if not os.path.exists(github_dir):
        os.makedirs(github_dir)

    app_github_dir = os.path.join(github_dir, app_name)

    if os.path.exists(app_github_dir):
        shutil.rmtree(app_github_dir)

    # Create a copy of the app
    shutil.copytree(app_path, app_github_dir)

    repo = git.Repo.init(app_github_dir)

    # Start working on the build

    actual_git = repo.git
    actual_git.checkout(b="tethysapp_warehouse_release")
    files_changed = False

    # Add the required files if they don't exist.

    workflows_path = os.path.join(app_github_dir, '.github', 'workflows')
    source_files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'application_files')
    if os.path.exists(workflows_path):
        shutil.rmtree(workflows_path)

    os.makedirs(workflows_path)

    recipe_path = os.path.join(app_github_dir, 'conda.recipes')

    if os.path.exists(recipe_path):
        shutil.rmtree(recipe_path)

    os.makedirs(recipe_path)

    source = os.path.join(source_files_path, 'getChannels.py')
    destination = os.path.join(recipe_path, 'getChannels.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'meta_template.yaml')
    destination = os.path.join(recipe_path, 'meta.yaml')
    filename = os.path.join(app_github_dir, 'setup.py')

    setup_py_data = parse_setup_py(filename)
    keywords = []
    email = ""

    try:
        # Dropping Keywords if it exists as they are already present in the main.yaml file
        keywords = setup_py_data.pop('keywords', None)
        email = setup_py_data["author_email"]

        # Clean up keywords
        keywords = keywords.replace('"', '').replace("'", '')
        if ',' in keywords:
            keywords = keywords.split(',')
        keywords = list(map(lambda x: x.strip(), keywords))

    except Exception as err:
        logger.error("Error ocurred while formatting keywords from setup.py")
        logger.error(err)

    template_data = {
        'metadataObj': json.dumps(setup_py_data).replace('"', "'")
    }

    apply_template(source, template_data, destination)

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'setup_helper.py')
    destination = os.path.join(app_github_dir, 'setup_helper.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    # Fix setup.py file to remove dependency on tethys

    rel_package = ""
    with fileinput.FileInput(filename, inplace=True) as f:
        for line in f:
            if "tethys_apps.app_installation" in line:
                print("from setup_helper import find_resource_files", end='\n')
            elif ("setup(" in line):
                print(
                    "resource_files += find_resource_files('tethysapp/' + app_package + '/scripts', 'tethysapp/' + app_package)", end='\n')
                print(line, end='')
            elif ("app_package = " in line):
                rel_package = line
                print(line, end='')
            else:
                print(line, end='')

    update_dependencies(app_github_dir, recipe_path, source_files_path, keywords, email)

    source = os.path.join(source_files_path, 'main_template.yaml')
    destination = os.path.join(workflows_path, 'main.yaml')
    app_name = rel_package.replace("app_package", '').replace("=", '').replace("'", "").strip()

    template_data = {
        'subject': "Tethys App Store: Build complete for " + app_name,
        'email': requester_email,
        'buildMsg': """
        Your Tethys App has been successfully built and is now available on the Tethys App Store.
        This is an auto-generated email and this email is not monitored for replies. Please send any queries to rohitkh@byu.edu
        """
    }
    apply_template(source, template_data, destination)

    # remove __init__.py file if present at top level

    init_path = os.path.join(app_github_dir, '__init__.py')

    if os.path.exists(init_path):
        os.remove(init_path)

    if LOCAL_DEBUG_MODE:
        logger.info("Completed Local Debug Processing for Git Repo")
        return JsonResponse({'status': "Completed local debugging"})

    # Check if this repo already exists on our remote:
    repo_name = app_name
    organization = g.get_organization("tethysapp")

    if repo_exists(repo_name, organization):
        # Delete the repo
        to_delete_repo = organization.get_repo(repo_name)
        to_delete_repo.delete()

    # Create the required repo:
    tethysapp_repo = organization.create_repo(
        repo_name,
        allow_rebase_merge=True,
        auto_init=False,
        description="For Tethys App Store Purposes",
        has_issues=False,
        has_projects=False,
        has_wiki=False,
        private=False,
    )

    remote_url = tethysapp_repo.git_url.replace("git://", "https://" + key + ":x-oauth-basic@")

    if 'tethysapp' in repo.remotes:
        logger.info("Remote already exists")
        tethysapp_remote = repo.remotes.tethysapp
        tethysapp_remote.set_url(remote_url)
    else:
        tethysapp_remote = repo.create_remote('tethysapp', remote_url)

    if files_changed:
        repo.git.add(A=True)
        repo.git.commit(m="Warehouse_Commit")

    tethysapp_remote.push('tethysapp_warehouse_release')

    tethysapp_repo = organization.get_repo(repo_name)

    workflowFound = False

    # Sometimes due to weird conda versioning issues the get_workflow_runs is not found
    # In that case return no value for the job_url and handle it in JS

    try:
        while not workflowFound:
            time.sleep(4)
            if tethysapp_repo.get_workflow_runs().totalCount > 0:
                logger.info("Obtained Workflow for Submission. Getting Job URL")

                try:
                    response = requests.get(tethysapp_repo.get_workflow_runs()[0].jobs_url, auth=('tethysapp', key))
                    response.raise_for_status()
                    jsonResponse = response.json()
                    workflowFound = jsonResponse["total_count"] > 0

                except HTTPError as http_err:
                    logger.error(f'HTTP error occurred while getting Jobs from GITHUB API: {http_err}')
                except Exception as err:
                    logger.error(f'Other error occurred while getting jobs from GITHUB API: {err}')

            if workflowFound:
                job_url = jsonResponse["jobs"][0]["html_url"]

        logger.info("Obtained Job URL: " + job_url)
    except AttributeError:
        logger.info("Unable to obtain Workflow Run")
        job_url = None

    return JsonResponse({'status': True,
                         'job_url': job_url,
                         'msg': "Application submitted successfully",
                         'url': tethysapp_repo.git_url.replace("git://", "https://")})


def update_dependencies(github_dir, recipe_path, source_files_path, keywords=[], email=""):
    install_yml = os.path.join(github_dir, 'install.yml')
    meta_yaml = os.path.join(source_files_path, 'meta_reqs.yaml')
    meta_extras = os.path.join(source_files_path, 'meta_extras.yaml')

    app_files_dir = os.path.join(recipe_path, '../tethysapp')

    app_folders = next(os.walk(app_files_dir))[1]
    app_scripts_path = os.path.join(app_files_dir, app_folders[0], 'scripts')

    Path(app_scripts_path).mkdir(parents=True, exist_ok=True)

    with open(install_yml) as f:
        install_yml_file = yaml.safe_load(f)

    with open(meta_yaml) as f:
        meta_yaml_file = yaml.safe_load(f)

    with open(meta_extras) as f:
        meta_extras_file = yaml.safe_load(f)

    meta_extras_file['extra']['author_email'] = email
    meta_extras_file['extra']['keywords'] = keywords

    meta_yaml_file['requirements']['run'] = install_yml_file['requirements']['conda']['packages']

    # Check if any pip dependencies are present

    if ("pip" in install_yml_file['requirements']):
        pip_deps = install_yml_file['requirements']["pip"]
        if pip_deps != None:
            logger.info("Pip dependencies found")
            pre_link = os.path.join(app_scripts_path, "install_pip.sh")
            pip_install_string = "pip install " + " ".join(pip_deps)
            with open(pre_link, "w") as f:
                f.write(pip_install_string)
                f.write('\necho "PIP Install Complete"')
            st = os.stat(pre_link)
            os.chmod(pre_link, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    with open(os.path.join(recipe_path, 'meta.yaml'), 'a') as f:
        yaml.safe_dump(meta_extras_file, f, default_flow_style=False)
        f.write("\n")
        yaml.safe_dump(meta_yaml_file, f, default_flow_style=False)


def repo_exists(repo_name, organization):

    try:
        repo = organization.get_repo(repo_name)
        logger.info("Repo Exists. Will have to delete")
        return True
    except Exception as e:
        logger.info("Repo doesn't exist")
        return False


def pull_git_repo(install_data, channel_layer, app_workspace):
    github_url = install_data.get("url")
    app_name = github_url.split("/")[-1].replace(".git", "")
    github_dir = os.path.join(app_workspace.path, 'gitsubmission')
    # create if github Dir does not exist
    if not os.path.exists(github_dir):
        os.makedirs(github_dir)

    app_github_dir = os.path.join(github_dir, app_name)

    if os.path.exists(app_github_dir):
        # Check if it is a github dir
        # Do a pull and then continue with branch selection
        repo = git.Repo(app_github_dir)
        origin = repo.remote(name='origin')

    else:
        os.mkdir(app_github_dir)
        repo = git.Repo.init(app_github_dir)
        origin = repo.create_remote('origin', github_url)

    origin.fetch()

    # Git has changed the default branch name to main so this next command might fail with git.exc.GitCommandError
    try:
        repo.git.checkout("master", "-f")
    except git.exc.GitCommandError:
        logger.info("Couldn't check out master branch. Attempting to checkout main")
        repo.git.checkout("main", "-f")

    origin.pull()
    remote_refs = repo.remote().refs
    branches = []
    for refs in remote_refs:
        branches.append(refs.name.replace("origin/", ""))

    get_data_json = {
        "data": {
            "branches": branches,
            "github_dir": app_github_dir
        },
        "jsHelperFunction": "showBranches",
        "helper": "addModalHelper"
    }
    send_notification(get_data_json, channel_layer)


def process_branch(install_data, channel_layer):
    repo = git.Repo(install_data['github_dir'])
    # Delete head if exists
    if 'tethysapp_warehouse_release' in repo.heads:
        logger.info("Deleting existing release branch")
        repo.delete_head('tethysapp_warehouse_release', '-D')

    origin = repo.remote(name='origin')
    repo.git.checkout(install_data['branch'])
    origin.pull()

    repo.create_head('tethysapp_warehouse_release')
    repo.git.checkout('tethysapp_warehouse_release')
    files_changed = False

    # Add the required files if they don't exist.

    workflows_path = os.path.join(install_data['github_dir'], '.github', 'workflows')
    source_files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'application_files')
    if os.path.exists(workflows_path):
        shutil.rmtree(workflows_path)

    os.makedirs(workflows_path)

    recipe_path = os.path.join(install_data['github_dir'], 'conda.recipes')

    if os.path.exists(recipe_path):
        shutil.rmtree(recipe_path)

    os.makedirs(recipe_path)

    source = os.path.join(source_files_path, 'getChannels.py')
    destination = os.path.join(recipe_path, 'getChannels.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'meta_template.yaml')
    destination = os.path.join(recipe_path, 'meta.yaml')
    filename = os.path.join(install_data['github_dir'], 'setup.py')

    setup_py_data = parse_setup_py(filename)
    keywords = []
    email = ""

    try:
        # Dropping Keywords if it exists as they are already present in the main.yaml file
        keywords = setup_py_data.pop('keywords', None)
        email = setup_py_data["author_email"]

        # Clean up keywords
        keywords = keywords.replace('"', '').replace("'", '')
        if ',' in keywords:
            keywords = keywords.split(',')
        keywords = list(map(lambda x: x.strip(), keywords))

    except Exception as err:
        logger.error("Error ocurred while formatting keywords from setup.py")
        logger.error(err)

    template_data = {
        'metadataObj': json.dumps(setup_py_data).replace('"', "'")
    }

    apply_template(source, template_data, destination)

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'setup_helper.py')
    destination = os.path.join(install_data['github_dir'], 'setup_helper.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    # Fix setup.py file to remove dependency on tethys

    rel_package = ""
    with fileinput.FileInput(filename, inplace=True) as f:
        for line in f:
            if "tethys_apps.app_installation" in line:
                print("from setup_helper import find_resource_files", end='\n')
            elif ("setup(" in line):
                print(
                    "resource_files += find_resource_files('tethysapp/' + app_package + '/scripts', 'tethysapp/' + app_package)", end='\n')
                print(line, end='')
            elif ("app_package = " in line):
                rel_package = line
                print(line, end='')
            else:
                print(line, end='')

    update_dependencies(install_data['github_dir'], recipe_path, source_files_path, keywords, email)

    source = os.path.join(source_files_path, 'main_template.yaml')
    destination = os.path.join(workflows_path, 'main.yaml')
    app_name = rel_package.replace("app_package", '').replace("=", '').replace("'", "").strip()

    template_data = {
        'subject': "Tethys App Store: Build complete for " + app_name,
        'email': install_data['email'],
        'buildMsg': """
        Your Tethys App has been successfully built and is now available on the Tethys App Store.
        This is an auto-generated email and this email is not monitored for replies. Please send any queries to rohitkh@byu.edu
        """
    }
    apply_template(source, template_data, destination)

    # remove __init__.py file if present at top level

    init_path = os.path.join(install_data['github_dir'], '__init__.py')

    if os.path.exists(init_path):
        os.remove(init_path)

    if LOCAL_DEBUG_MODE:
        logger.info("Completed Local Debug Processing for Git Repo")
        return

    # Check if this repo already exists on our remote:
    repo_name = install_data['github_dir'].split('/')[-1]
    organization = g.get_organization("tethysapp")

    if repo_exists(repo_name, organization):
        # Delete the repo
        to_delete_repo = organization.get_repo(repo_name)
        to_delete_repo.delete()

    # Create the required repo:
    tethysapp_repo = organization.create_repo(
        repo_name,
        allow_rebase_merge=True,
        auto_init=False,
        description="For Tethys App Store Purposes",
        has_issues=False,
        has_projects=False,
        has_wiki=False,
        private=False,
    )

    remote_url = tethysapp_repo.git_url.replace("git://", "https://" + key + ":x-oauth-basic@")

    if 'tethysapp' in repo.remotes:
        logger.info("Remote already exists")
        tethysapp_remote = repo.remotes.tethysapp
        tethysapp_remote.set_url(remote_url)
    else:
        tethysapp_remote = repo.create_remote('tethysapp', remote_url)

    if files_changed:
        repo.git.add(A=True)
        repo.git.commit(m="Warehouse_Commit")

    tethysapp_remote.push('tethysapp_warehouse_release')

    tethysapp_repo = organization.get_repo(repo_name)

    workflowFound = False

    # Sometimes due to weird conda versioning issues the get_workflow_runs is not found
    # In that case return no value for the job_url and handle it in JS

    try:
        while not workflowFound:
            time.sleep(4)
            if tethysapp_repo.get_workflow_runs().totalCount > 0:
                logger.info("Obtained Workflow for Submission. Getting Job URL")

                try:
                    response = requests.get(tethysapp_repo.get_workflow_runs()[0].jobs_url, auth=('tethysapp', key))
                    response.raise_for_status()
                    jsonResponse = response.json()
                    workflowFound = jsonResponse["total_count"] > 0

                except HTTPError as http_err:
                    logger.error(f'HTTP error occurred while getting Jobs from GITHUB API: {http_err}')
                except Exception as err:
                    logger.error(f'Other error occurred while getting jobs from GITHUB API: {err}')

            if workflowFound:
                job_url = jsonResponse["jobs"][0]["html_url"]

        logger.info("Obtained Job URL: " + job_url)
    except AttributeError:
        logger.info("Unable to obtain Workflow Run")
        job_url = None

    get_data_json = {
        "data": {
            "githubURL": tethysapp_repo.git_url.replace("git:", "https:"),
            "job_url": job_url
        },
        "jsHelperFunction": "addComplete",
        "helper": "addModalHelper"
    }
    send_notification(get_data_json, channel_layer)
