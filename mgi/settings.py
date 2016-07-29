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
from mongoengine import connect

VERSION = "BETA"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if DEBUG:
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
    
    # os.environ['HTTPS'] = "on"
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

#SMTP Configuration
USE_EMAIL = False #Send email, True or False
SERVER_EMAIL = 'noreply@nmrr.org'
ADMINS = [('admin', 'admin@nmrr.org')]
MANAGERS = [('manager', 'moderator@nmrr.org'),]
EMAIL_SUBJECT_PREFIX = "[NMRR] "

#Password Policy
# Determines wether to use the password history.
PASSWORD_USE_HISTORY = True
# A list of raw strings representing paths to ignore while checking if a user has to change his/her password.
PASSWORD_CHANGE_MIDDLEWARE_EXCLUDED_PATHS = []
# Specifies the number of user's previous passwords to remember when the password history is being used.
PASSWORD_HISTORY_COUNT = 1
# Determines after how many seconds a user is forced to change his/her password.
PASSWORD_DURATION_SECONDS = 24 * 90 * 3600
# Don't log the person out in the middle of a session. Only do the checks at login time.
PASSWORD_CHECK_ONLY_AT_LOGIN = True
# Specifies the minimum length for passwords.
PASSWORD_MIN_LENGTH = 12
# Specifies the minimum amount of required letters in a password.
PASSWORD_MIN_LETTERS = 3
# Specifies the minimum amount of required uppercase letters in a password.
PASSWORD_MIN_UPPERCASE_LETTERS = 1
# Specifies the minimum amount of required lowercase letters in a password.
PASSWORD_MIN_LOWERCASE_LETTERS = 1
# Specifies the minimum amount of required numbers in a password.
PASSWORD_MIN_NUMBERS = 1
# Specifies the minimum amount of required symbols in a password.
PASSWORD_MIN_SYMBOLS = 1
# Specifies a list of common sequences to attempt to match a password against.
PASSWORD_COMMON_SEQUENCES = [u'0123456789', u'`1234567890-=', u'~!@#$%^&*()_+', u'abcdefghijklmnopqrstuvwxyz',
                             u"quertyuiop[]\\asdfghjkl;'zxcvbnm,./", u'quertyuiop{}|asdfghjkl;"zxcvbnm<>?',
                             u'quertyuiopasdfghjklzxcvbnm', u"1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
                             u'qazwsxedcrfvtgbyhnujmikolp']
# A minimum distance of the difference between old and new password. A positive integer.
# Values greater than 1 are recommended.
PASSWORD_DIFFERENCE_DISTANCE = 3
# Specifies the maximum amount of consecutive characters allowed in passwords.
PASSWORD_MAX_CONSECUTIVE = 3
# A list of project specific words to check a password against.
PASSWORD_WORDS = []

# Replace by your own values
MONGO_MGI_USER = "mgi_user"
MONGO_MGI_PASSWORD = "mgi_password"
MGI_DB = "mgi"
MONGODB_URI = "mongodb://" + MONGO_MGI_USER + ":" + MONGO_MGI_PASSWORD + "@localhost/" + MGI_DB
connect(MGI_DB, host=MONGODB_URI)

# BLOB Hoster module parameters
BLOB_HOSTER = 'GridFS'
BLOB_HOSTER_URI = MONGODB_URI
BLOB_HOSTER_USER = MONGO_MGI_USER
BLOB_HOSTER_PSWD = MONGO_MGI_PASSWORD
MDCS_URI = 'http://127.0.0.1:8000'

#Celery configuration
USE_BACKGROUND_TASK = False
BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}
BROKER_TRANSPORT_OPTIONS = {'fanout_patterns': True}

# Handle system module parameters
HANDLE_SERVER_URL = ''
HANDLE_SERVER_SCHEMA = ''
HANDLE_SERVER_USER = ''
HANDLE_SERVER_PSWD = ''

# Customization: Registry
CUSTOM_TITLE = 'Materials Resource Registry'
CUSTOM_ORGANIZATION = ''
CUSTOM_NAME = 'NMRR'
CUSTOM_SUBTITLE = 'Part of the Materials Genome Initiative'
CUSTOM_DATA = 'Materials Data'
CUSTOM_CURATE = 'Add your resource'
CUSTOM_EXPLORE = 'Search for resources'
CUSTOM_URL = '#'

# OAI_PMH parameters
OAI_ADMINS = (
    ('Administrator', 'admin@nmrr.com'),
)
HOST = '127.0.0.1'
OAI_HOST_URI = MDCS_URI
OAI_NAME = CUSTOM_NAME + ' ' + HOST
OAI_DELIMITER = ':'
OAI_DESCRIPTION = 'OAI-PMH ' + CUSTOM_NAME
OAI_GRANULARITY = 'YYYY-MM-DDThh:mm:ssZ' #the finest harvesting granularity supported by the repository
OAI_PROTOCOLE_VERSION = '2.0' #the version of the OAI-PMH supported by the repository
OAI_SCHEME = 'oai'
OAI_REPO_IDENTIFIER = 'server-' + HOST
OAI_SAMPLE_IDENTIFIER = OAI_SCHEME+OAI_DELIMITER+OAI_REPO_IDENTIFIER+OAI_DELIMITER+'id/12345678a123aff6ff5f2d9e'
OAI_DELETED_RECORD = 'persistent' #no ; transient ; persistent

# PARSER
PARSER_MIN_TREE = True
PARSER_IGNORE_MODULES = False
PARSER_COLLAPSE = True
PARSER_AUTO_KEY_KEYREF = True
PARSER_IMPLICIT_EXTENSION_BASE = False

TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'templates')
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "utils.custom_context_processors.domain_context_processor",
    #"password_policies.context_processors.password_status",
    'mgi.context_processors.password_status',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'mongoengine.django.mongo_auth',
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
    'user_dashboard',
    'oai_pmh',
    'testing',
    'utils.XSDParser',
    'password_policies'
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
    "exclude_namespaces": ['error_redirect', 'ping'],  # List URL namespaces to ignore
    "api_version": '1.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '',  # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}


# django.contrib.auth.views.login redirects you to accounts/profile/ 
# right after you log in by default. This setting changes that.
LOGIN_REDIRECT_URL = '/'

SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # https://docs.djangoproject.com/en/dev/howto/auth-remote-user/
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'password_policies.middleware.PasswordChangeMiddleware',
    'mgi.middleware.PasswordChangeMiddleware',
)

ROOT_URLCONF = 'mgi.urls'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

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
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
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
