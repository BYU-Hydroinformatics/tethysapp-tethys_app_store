import git
import os
import shutil
import github

from .app import Warehouse as app

g = github.Github("9ce86ef819762c208341f3346376e608bb4ac8b6")


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
    files_changed = False

    # Add the required files if they don't exist.

    workflows_path = os.path.join(installData['github_dir'], '.github', 'workflows')
    source_files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'application_files')
    if not os.path.exists(workflows_path):
        os.makedirs(workflows_path)

    source = os.path.join(source_files_path, 'main.yaml')
    destination = os.path.join(workflows_path, 'main.yaml')

    if not os.path.exists(destination):
        files_changed = True
        shutil.copyfile(source, destination)

    recipe_path = os.path.join(installData['github_dir'], 'conda.recipes')

    if not os.path.exists(recipe_path):
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

    repo.create_head('tethysapp_warehouse_release')
    if files_changed:
        repo.git.add(A=True)
        repo.git.commit(m="Warehouse Commit")

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
