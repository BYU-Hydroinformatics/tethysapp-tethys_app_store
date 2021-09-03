# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
import os
from unittest import mock

from django.conf import settings
import django

# Mock Dependencies
# NOTE: No obvious way to automatically anticipate all the sub modules without
# installing the package, which is what we are trying to avoid.
MOCK_MODULES = [
    'bokeh', 'bokeh.core.templates', 'bokeh.document', 'bokeh.embed', 'bokeh.embed.elements', 'bokeh.embed.util',
    'bokeh.resources', 'bokeh.server.django', 'bokeh.server.django.consumers', 'bokeh.util.compiler',
    'channels',
    'conda', 'conda.cli', 'conda.cli.python_api',
    'condorpy',
    'django_gravatar',
    'dask', 'dask.delayed', 'dask.distributed',
    'distributed', 'distributed.protocol', 'distributed.protocol.serialize',
    'distro',
    'docker', 'docker.types', 'docker.errors',
    'guardian', 'guardian.admin', 'guardian.models', 'guardian.shortcuts',
    'model_utils', 'model_utils.managers',
    'plotly', 'plotly.offline', 'plotly.graph_objects',
    'siphon', 'siphon.catalog', 'siphon.http_util',
    'social_core', 'social_core.exceptions',
    'social_django',
    'sqlalchemy', 'sqlalchemy.orm', 'sqlalchemy.sql', 'sqlalchemy.types', 'sqlalchemy.dialects',
    'sqlalchemy.dialects.postgresql', 'sqlalchemy.dialects.postgresql.base', 'sqlalchemy.sql.expression',
    'sqlalchemy.ext',
    'tethys_apps.harvester', 'tethys_apps.models',  # Mocked to prevent issues with loading apps during docs build.
    'tethys_compute.utilities',  # Mocked to prevent issues with DictionaryField and List Field during docs build.
    'yaml'
]


# Mock dependency modules so we don't have to install them
# See: https://docs.readthedocs.io/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
class MockModule(mock.MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return mock.MagicMock()


print('NOTE: The following modules are mocked to prevent timeouts during the docs build process on RTD:')
print('{}'.format(', '.join(MOCK_MODULES)))
sys.modules.update((mod_name, MockModule()) for mod_name in MOCK_MODULES)
sys.path.insert(0, os.path.abspath('.'))
autodoc_mock_imports = ["django", "sqlalchemy", "geoalchemy2"]

installed_apps = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tethys_config',
    'tethys_quotas',
    'tethys_apps',
    'tethys_gizmos',
    'tethys_services',
    'tethys_compute',
]
settings.configure(INSTALLED_APPS=installed_apps)
django.setup()
# -- Project information -----------------------------------------------------

project = 'Groundwater Data Mapper'
copyright = '2020, Sarva Pulla/Brigham Young University'
author = 'Sarva Pulla/Brigham Young University'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinxcontrib.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
