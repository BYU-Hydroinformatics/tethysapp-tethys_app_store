import os


def find_resource_files(directory, relative_to=None):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if relative_to is not None:
                paths.append(os.path.join(os.path.relpath(path, relative_to), filename))
            else:
                paths.append(os.path.join('..', path, filename))
    return paths
    
def find_resource_files_of_type(resource_type, app_package, app_root):
    relative_to = f"{app_root}/{app_package}"
    resources = find_resource_files(f"{relative_to}/{resource_type}", relative_to)
    return resources


def find_all_resource_files(app_package, app_root):
    resources = find_resource_files_of_type("templates", app_package, app_root)
    resources += find_resource_files_of_type("public", app_package, app_root)
    resources += find_resource_files_of_type("workspaces", app_package, app_root)
    resources += find_resource_files_of_type("scripts", app_package, app_root)

    return resources