################################################################################
#
# File Name: settings.py
# Application: mgi
# Description: 
#   Django settings for mgi project.
#   For more information on this file, see
#   https://docs.djangoproject.com/en/1.7/topics/settings/
#
#   For the full list of settings and their values, see
#   https://docs.djangoproject.com/en/1.7/ref/settings/
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import os

VERSION = "alpha"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


if DEBUG == True:
    SECRET_KEY = 'ponq)(gd8hm57799)$lup4g9kyvp0l(9)k-3!em7dddn^(y)!5'
    
    ALLOWED_HOSTS = ['*']
    
    DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
         }
    }
    
else:
    pass
    # Uncomment and set all parameters, delete pass instruction
    # See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/
    
    # https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key
    # SECRET_KEY = '<secret_key>'
    
    # https://docs.djangoproject.com/en/1.7/ref/settings/#allowed-hosts
    # ALLOWED_HOSTS = ['<domain>','<server_ip>']
    
    #os.environ['HTTPS'] = "on"
    # https://docs.djangoproject.com/en/1.7/ref/settings/#csrf-cookie-secure
    # CSRF_COOKIE_SECURE = True
    # https://docs.djangoproject.com/en/1.7/ref/settings/#session-cookie-secure
    # SESSION_COOKIE_SECURE = True
    
    # https://docs.djangoproject.com/en/1.7/ref/settings/#databases
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #         'USER':"<postgres_user>",
    #         'PASSWORD': "<postgres_password>",
    #         'NAME': 'mgi',                      
    #     }
    # }

# Replace by your own values
from mongoengine import connect
MONGO_MGI_USER = "mgi_user"
MONGO_MGI_PASSWORD = "mgi_password"
MONGODB_URI = "mongodb://" + MONGO_MGI_USER + ":" + MONGO_MGI_PASSWORD + "@localhost/mgi"
connect("mgi", host=MONGODB_URI)

# BLOB Hoster module parameters
BLOB_HOSTER = 'GridFS'
BLOB_HOSTER_URI = MONGODB_URI
BLOB_HOSTER_USER = MONGO_MGI_USER
BLOB_HOSTER_PSWD = MONGO_MGI_PASSWORD
MDCS_URI = 'http://127.0.0.1:8000'

# Handle system module parameters
HANDLE_SERVER_URL = ''
HANDLE_SERVER_SCHEMA = ''
HANDLE_SERVER_USER = ''
HANDLE_SERVER_PSWD = ''

# Customization: Registry
CUSTOM_TITLE = 'Materials Resource Registry'
CUSTOM_SUBTITLE = 'Part of the Materials Genome Initiative'
CUSTOM_DATA = 'Materials Data' 
CUSTOM_CURATE = 'Add your resource' 
CUSTOM_EXPLORE = 'Search for resources'

#CURATE
CURATE_MIN_TREE = True
CURATE_COLLAPSE = False

#KEYWORD
EXPLORE_BY_KEYWORD = True  #True or False

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.request",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"utils.custom_context_processors.domain_context_processor")

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mongoengine.django.mongo_auth',
    'rest_framework',
    'rest_framework_swagger',
    'oauth2_provider',
    'admin_mdcs',
    'api',
    'curate',
    'exporter',
    'explore',
    'compose',
    'modules',
)

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 31536000
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    )
    # ,
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # )
}

SWAGGER_SETTINGS = {
    "exclude_namespaces": ['error_redirect','ping'], # List URL namespaces to ignore
    "api_version": '1.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '', # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}


# django.contrib.auth.views.login redirects you to accounts/profile/ 
# right after you log in by default. This setting changes that.
LOGIN_REDIRECT_URL = '/'

SESSION_SAVE_EVERY_REQUEST=True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',  # https://docs.djangoproject.com/en/dev/howto/auth-remote-user/
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mgi.urls'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

# python manage.py collectstatic gathers all static files in this directory
# link this directory to static in apache configuration file
STATIC_ROOT = 'var/www/mgi/static/'

# static files manually added
STATIC_URL = '/static/'

# static files gathered
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Logging
# https://docs.djangoproject.com/en/1.7/topics/logging/

SITE_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..').replace('\\', '/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {  # use 'MYAPP' to make it app specific
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}