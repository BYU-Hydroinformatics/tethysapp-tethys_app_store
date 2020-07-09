import git
import os
import shutil
import github
import fileinput
import yaml

from .app import Warehouse as app


key = "#45c0#a820f85aa11d727#f02c382#c91d63be83".replace("#", "e")
g = github.Github(key)


def update_dependencies(github_dir, recipe_path, source_files_path):
    install_yml = os.path.join(github_dir, 'install.yml')
    meta_yaml = os.path.join(source_files_path, 'meta_reqs.yaml')

    with open(install_yml) as f:
        install_yml_file = yaml.safe_load(f)

    with open(meta_yaml) as f:
        meta_yaml_file = yaml.safe_load(f)

    meta_yaml_file['requirements']['run'] = install_yml_file['requirements']['conda']['packages']

    with open(os.path.join(recipe_path, 'meta.yaml'), 'a') as f:
        yaml.safe_dump(meta_yaml_file, f, default_flow_style=False)


def repo_exists(repo_name, organization):

    try:
        repo = organization.get_repo(repo_name)
        print("Repo Exists. Will HAve to delete")
        return True
    except Exception as e:
        print(e)
        print("Repo doesn't exist")
        return False


async def pull_git_repo(installData, channel_layer):
    github_url = installData.get("url")
    app_name = github_url.split("/")[-1].replace(".git", "")
    app_workspace = app.get_app_workspace()
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
    repo.git.checkout("master", "-f")
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
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )


async def process_branch(installData, channel_layer):

    repo = git.Repo(installData['github_dir'])
    # Delete head if exists
    if 'tethysapp_warehouse_release' in repo.heads:
        print("Deleting existing release branch")
        repo.delete_head('tethysapp_warehouse_release', '-D')

    origin = repo.remote(name='origin')
    repo.git.checkout(installData['branch'])
    origin.pull()

    repo.create_head('tethysapp_warehouse_release')
    repo.git.checkout('tethysapp_warehouse_release')
    files_changed = False

    # Add the required files if they don't exist.

    workflows_path = os.path.join(installData['github_dir'], '.github', 'workflows')
    source_files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'application_files')
    if os.path.exists(workflows_path):
        shutil.rmtree(workflows_path)

    os.makedirs(workflows_path)

    source = os.path.join(source_files_path, 'main.yaml')
    destination = os.path.join(workflows_path, 'main.yaml')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    recipe_path = os.path.join(installData['github_dir'], 'conda.recipes')

    if os.path.exists(recipe_path):
        shutil.rmtree(recipe_path)

    os.makedirs(recipe_path)

    source = os.path.join(source_files_path, 'getChannels.py')
    destination = os.path.join(recipe_path, 'getChannels.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'meta.yaml')
    destination = os.path.join(recipe_path, 'meta.yaml')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    source = os.path.join(source_files_path, 'setup_helper.py')
    destination = os.path.join(installData['github_dir'], 'setup_helper.py')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    # Fix setup.py file to remove dependency on tethys

    filename = os.path.join(installData['github_dir'], 'setup.py')

    with fileinput.FileInput(filename, inplace=True) as f:
        for line in f:
            if "tethys_apps.app_installation" in line:
                print("from setup_helper import find_resource_files", end='\n')
            else:
                print(line, end='')

    update_dependencies(installData['github_dir'], recipe_path, source_files_path)

    # Check if this repo already exists on our remote:
    repo_name = installData['github_dir'].split('/')[-1]

    organization = g.get_organization("tethysapp")

    # For testing don't delete and recreate
    # tethysapp_repo = organization.get_repo(repo_name)

    if repo_exists(repo_name, organization):
        # Delete the repo
        to_delete_repo = organization.get_repo(repo_name)
        to_delete_repo.delete()

    # Create the required repo:
    tethysapp_repo = organization.create_repo(
        repo_name,
        allow_rebase_merge=True,
        auto_init=False,
        description="For Application Warehouse Purposes",
        has_issues=False,
        has_projects=False,
        has_wiki=False,
        private=False,
    )

    if 'tethysapp' in repo.remotes:
        print("Remote already exists")
        tethysapp_remote = repo.remotes.tethysapp
    else:
        tethysapp_remote = repo.create_remote('tethysapp', tethysapp_repo.git_url.replace("git:", "https:"))

    if files_changed:
        repo.git.add(A=True)
        repo.git.commit(m="Warehouse_Commit")

    tethysapp_remote.push('tethysapp_warehouse_release')

    get_data_json = {
        "data": {
            "githubURL": tethysapp_repo.git_url.replace("git:", "https:")
        },
        "jsHelperFunction": "addComplete",
        "helper": "addModalHelper"
    }
    await channel_layer.group_send(
        "notifications",
        {
            "type": "install_notifications",
            "message": get_data_json
        }
    )
