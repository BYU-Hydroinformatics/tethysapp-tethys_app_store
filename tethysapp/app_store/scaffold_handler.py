import os
import re
import json
import shutil

from jinja2 import Template
from subprocess import (Popen, PIPE, STDOUT)
from pathlib import Path

from .git_install_handlers import write_logs
from .helpers import logger, get_override_key, run_process
from tethys_cli.scaffold_commands import APP_PATH, APP_PREFIX, get_random_color, render_path, TEMPLATE_SUFFIX
from tethys_cli.cli_helpers import get_manage_path

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from tethys_sdk.routing import controller


def install_app(app_path):
    logger.info("Running scaffolded application install....")
    process = Popen(['tethys', 'install', "-d", "-q"],
                    cwd=app_path, stdout=PIPE, stderr=STDOUT)
    write_logs(logger, process.stdout, 'Python Install SubProcess: ')
    exitcode = process.wait()
    logger.info("Python Application install exited with: " + str(exitcode))

    manage_path = get_manage_path({})
    logger.info("Running Tethys Collectall")
    intermediate_process = ['python', manage_path, 'pre_collectstatic']
    run_process(intermediate_process)
    # Setup for main collectstatic
    intermediate_process = ['python', manage_path, 'collectstatic', '--noinput']
    run_process(intermediate_process)
    # Run collectworkspaces command
    intermediate_process = ['python', manage_path, 'collectworkspaces',  '--force']
    run_process(intermediate_process)


def get_develop_dir(app_workspace):
    workspace_directory = app_workspace.path
    dev_dir = os.path.join(workspace_directory, 'develop')
    if not os.path.exists(dev_dir):
        os.mkdir(dev_dir)

    return dev_dir


def proper_name_validator(value, default):
    """
    Validate proper_name user input.
    """
    # Check for default
    if value == default:
        return True, value

    # Validate and sanitize user input
    proper_name_error_regex = re.compile(r'^[a-zA-Z0-9\s]+$')
    proper_name_warn_regex = re.compile(r'^[a-zA-Z0-9-\s_\"\']+$')

    if not proper_name_error_regex.match(value):
        # If offending characters are dashes, underscores or quotes, replace and notify user
        if proper_name_warn_regex.match(value):
            value = value.replace('_', ' ')
            value = value.replace('-', ' ')
            value = value.replace('"', '')
            value = value.replace("'", "")
        # Otherwise, throw error
        else:
            return False, value
    return True, value


@api_view(['POST'])
@permission_classes((AllowAny,))
@controller(
    name='scaffold_app',
    url='app-store/scaffold',
    app_workspace=True,
    login_required=False
)
@csrf_exempt
@controller(
    name='scaffold_app',
    url='app-store/scaffold',
    app_workspace=True,
)
def scaffold_command(request, app_workspace):
    """
    Create a new Tethys app projects in the workspace dir. based on an API Call to the app store
    Need to have the custom GitHub API Key present

    Input JSON Object:

    {
                name: "newName",
                proper_name: " my First APP",
                description: "Description",
                tags: "",
                author_name: "",
                author_email: "",
                license_name: "",
                overwrite: true/false (defaults to false)
    }

    """

    override_key = get_override_key()
    if(request.GET.get('custom_key') != override_key):
        return HttpResponse('Unauthorized', status=401)

    # Set ScaffoldRunning file to prevent auto restart from the filewatchers
    workspace_directory = app_workspace.path

    install_status_dir = os.path.join(workspace_directory, 'install_status')

    if not os.path.exists(install_status_dir):
        os.makedirs(install_status_dir)

    Path(os.path.join(workspace_directory, 'install_status', 'scaffoldRunning')).touch()

    received_json_data = json.loads(request.body)

    # Get template dirs
    logger.debug('APP_PATH: {}'.format(APP_PATH))
    template_name = 'default'
    template_root = os.path.join(APP_PATH, 'default')

    logger.debug('Template root directory: {}'.format(template_root))

    # Validate template
    if not os.path.isdir(template_root):
        return JsonResponse({'status': 'false', 'message': 'Error: "{}" is not a valid template.'.format(
            template_name)}, status=400)

    # Validate project name
    project_name = received_json_data.get('name')

    # Only lowercase
    contains_uppers = False
    for letter in project_name:
        if letter.isupper():
            contains_uppers = True
            break

    if contains_uppers:
        project_name = project_name.lower()

    # Check for valid characters name
    project_error_regex = re.compile(r'^[a-zA-Z0-9_]+$')
    project_warning_regex = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Only letters, numbers and underscores allowed in app names
    if not project_error_regex.match(project_name):
        # If the only offending character is a dash, replace dashes with underscores and notify user
        if project_warning_regex.match(project_name):
            project_name = project_name.replace('-', '_')
        # Otherwise, throw error
        else:
            error_msg = 'Error: Invalid characters in project name "{0}".Only letters, numbers, and underscores.'.format(project_name) # noqa E501
            return JsonResponse({'status': 'false', 'message': error_msg}, status=400)

    # Project name derivatives
    project_dir = '{0}-{1}'.format(APP_PREFIX, project_name)
    split_project_name = project_name.split('_')
    title_case_project_name = [x.title() for x in split_project_name]
    default_proper_name = ' '.join(title_case_project_name)
    class_name = ''.join(title_case_project_name)
    default_theme_color = get_random_color()

    proper_name = received_json_data.get("proper_name", default_proper_name)

    # Validate Proper Name

    is_name_valid, proper_name = proper_name_validator(proper_name, default_proper_name)
    if not is_name_valid:
        error_msg = 'Error: Proper name can only contain letters and numbers and spaces.'
        return JsonResponse({'status': 'false', 'message': error_msg}, status=400)

    # Build up template context
    context = {
        'project': project_name,
        'project_dir': project_dir,
        'project_url': project_name.replace('_', '-'),
        'class_name': class_name,
        'proper_name': proper_name,
        'description': received_json_data.get("description", ""),
        'color': default_theme_color,
        'tags': received_json_data.get("tags", ''),
        'author': received_json_data.get("author_name", ""),
        'author_email': received_json_data.get("author_email", ""),
        'license_name': received_json_data.get("license_name", "")
    }

    logger.debug('Template context: {}'.format(context))

    # Create root directory
    dev_dir = get_develop_dir(app_workspace)
    project_root = os.path.join(dev_dir, project_dir)
    logger.debug('Project root path: {}'.format(project_root))

    overwrite_if_exists = received_json_data.get("overwrite", False)

    if os.path.isdir(project_root):
        if overwrite_if_exists:
            try:
                shutil.rmtree(project_root)
            except OSError:
                error_msg = ('Error: Unable to overwrite "{}". '
                             'Please remove the directory and try again.'.format(project_root))
                return JsonResponse({'status': 'false', 'message': error_msg}, status=400)
        else:
            error_msg = ('Error: App directory exists "{}". '
                         'and Overwrite was not permitted. Please remove the directory and try again.'.format(
                             project_root))
            return JsonResponse({'status': 'false', 'message': error_msg}, status=400)

    # Walk the template directory, creating the templates and directories in the new project as we go
    for curr_template_root, dirs, template_files in os.walk(template_root):
        curr_project_root = curr_template_root.replace(template_root, project_root)
        curr_project_root = render_path(curr_project_root, context)

        # Create Root Directory
        os.makedirs(curr_project_root)

        # Create Files
        for template_file in template_files:
            template_file_path = os.path.join(curr_template_root, template_file)
            project_file = template_file.replace(TEMPLATE_SUFFIX, '')
            project_file_path = os.path.join(curr_project_root, project_file)

            # Load the template
            logger.debug('Loading template: "{}"'.format(template_file_path))

            try:
                with open(template_file_path, 'r') as tfp:
                    template = Template(tfp.read())
            except UnicodeDecodeError:
                with open(template_file_path, 'br') as tfp:
                    with open(project_file_path, 'bw') as pfp:
                        pfp.write(tfp.read())
                continue

            # Render template if loaded
            logger.debug('Rendering template: "{}"'.format(template_file_path))
            if template:
                with open(project_file_path, 'w') as pfp:
                    pfp.write(template.render(context))

    install_app(project_root)

    # Check if Scaffold Running file is present and delete it
    scaffold_running_path = os.path.join(workspace_directory, 'install_status', 'scaffoldRunning')
    if os.path.exists(scaffold_running_path):
        os.remove(scaffold_running_path)

    return JsonResponse({'status': 'true', 'message': "App Scaffolded"}, status=200)
