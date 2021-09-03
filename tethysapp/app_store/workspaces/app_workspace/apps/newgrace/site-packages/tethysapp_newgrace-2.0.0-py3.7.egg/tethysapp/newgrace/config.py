import os
from .app import Newgrace as app

app_workspace = app.get_app_workspace()
app_wksp_path = os.path.join(app_workspace.path, '')
BASE_PATH = app_wksp_path
SHELL_DIR = BASE_PATH + 'shell/'
SHAPE_DIR = BASE_PATH + 'shape/'


def get_thredds_url():
    return app.get_custom_setting("Thredds wms URL")


def get_global_netcdf_dir():
    return app.get_custom_setting("Local Thredds Folder Path")
