import sys
sys.path.append('/home/gio/tethysdev/tethys/tethys_portal')

from tethys_portal.settings import *

# DATABASES = { 
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": "memory:", 
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tethys_platform',
        'USER': 'tethys_super',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': '5436'
    }
}