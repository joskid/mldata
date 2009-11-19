# Django settings for mldata project.

PRODUCTION = False # set to True when project goes live

if not PRODUCTION:
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
else:
    DEBUG = False


ADMINS = (
    ('Sebastian Henschel', 'shogun@kodeaffe.de'),
    ('Soeren Sonnenburg', 'Soeren.Sonnenburg@tu-berlin.de'),
    ('Mikio Braun', 'mikio@cs.tu-berlin.de'),
)

MANAGERS = ADMINS

if PRODUCTION:
    DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'mldata'             # Or path to database file if using sqlite3.
else:
    DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'mldata.db'             # Or path to database file if using sqlite3.

DATABASE_USER = 'mldata'             # Not used with sqlite3.
DATABASE_PASSWORD = 'XXXXXXXXX'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


# on production server, path has to be inserted in django.wsgi
if not PRODUCTION:
	import os
	import sys
	PROJECT_ROOT = os.path.dirname(__file__)
	sys.path.insert(0, os.path.join(PROJECT_ROOT, 'utils'))

# in which directory the the data is actually saved 
# as files
if PRODUCTION:
	DATAPATH = '/home/mldata/data'
else:
	DATAPATH = 'media/data'

# Tagging stuff
#FORCE_LOWERCASE_TAGS = 'False'
#MAX_TAG_LENGTH = 30
TAG_SPLITCHAR = ','


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media_admin/'


# needed for registration
SITE_ID = 1
LOGIN_REDIRECT_URL='/'
ACCOUNT_ACTIVATION_DAYS=1
#DEFAULT_FROM_EMAIL='admin@mldata.org'
DEFAULT_FROM_EMAIL='mldata@data.ml.tu-berlin.de'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '67-0bxcy%$$&1%=9@1(@g0xxgsx)0jf^i=5@lf!i44ivp$k)mk'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'mldata.urls'

if PRODUCTION:
	TEMPLATE_DIRS = (
		'/home/mldata/django/mldata/templates/',
	)
else:
	TEMPLATE_DIRS = (
		'templates/',
	)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.markup',
    'django.contrib.humanize',
    'mldata',
    'mldata.about',
    'mldata.blog',
    'mldata.forum',
    'mldata.registration',
    'mldata.user',
    'mldata.repository',
    'mldata.tagging',
)
