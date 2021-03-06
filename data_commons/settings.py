"""
Django settings for data_commons project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import environ
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR = environ.Path(__file__) - 2

env = environ.Env(DEBUG=(bool, True),) # set default values and casting
root = environ.Path(BASE_DIR)

#copy AWS_* to config
l = locals()
for key, value in env.ENVIRON.items():
    if key.startswith('AWS_'):
        l[key] = value

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
PRODUCTION = env('PRODUCTION', default=not DEBUG)

TEST_RUNNER = 'data_commons.runner.PytestTestRunner'


# SECURITY WARNING: keep the secret key used in production secret!
if PRODUCTION:
    SECRET_KEY = env('SECRET_KEY')
else:
    SECRET_KEY = env('SECRET_KEY',
        default='4fagvff=svoxxk-$q+76yk01nf*_0s%m9nas@7t4)75*2dy=%p')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]
ALLOWED_HOSTS += env.list('ALLOWED_HOSTS', default=[])

# Application definition

INSTALLED_APPS = [
    #these need to be imported first
    'apps.profiles',
    'djangocms_admin_style',

    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.postgres',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    #3rd-party
    'actstream',
    'aldryn_bootstrap3',
    'anymail',
    'autofixture',
    'badgify',
    'bootstrap3',
    'bootstrap_pagination',
    'ckeditor',
    'ckeditor_uploader',
    'django_bootstrap_breadcrumbs',
    'django_comments',
    'django_comments_xtd',
    'django_fsm',
    'django_rq',
    'django_select2',
    #'flag',
    'fsm_admin',
    'haystack',
    'imagekit',
    'import_export',
    'mptt',
    'rest_framework',
    'taggit',

    #ours
    'apps.datasets',
    'apps.focus',
    'apps.stories',

    #cms
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'image_cropping',
    'djangocms_column',
    'djangocms_forms',
    'djangocms_link',
    #'djangocms_file',
    #'djangocms_picture',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_image',
    'cmsplugin_filer_utils',
    'djangocms_style',
    'djangocms_snippet',
    'djangocms_googlemap',
    'djangocms_video',

    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'data_commons.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ str(root.path('templates')) ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

if PRODUCTION:
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]


WSGI_APPLICATION = 'data_commons.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': env.db_url('DATABASE_URL',
        default='sqlite://'+str(root.path('db.sqlite3')))
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SEESION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
#STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    str(root.path('static/')),
]

STATIC_ROOT = str(root.path('public/static/'))
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = str(root.path('public/media/'))

ALDJEMY_ENGINES = {
    'postgis': 'postgresql',
}

HAYSTACK_CONNECTIONS = {
    'default': env.search_url('SEARCH_URL', default='simple://'),
}

USE_AWS_ELASTICSEARCH = 'es.amazonaws.com' in env('SEARCH_URL', default='')

if USE_AWS_ELASTICSEARCH:
    import elasticsearch
    from requests_aws4auth import AWS4Auth

    elasticsearch_kwargs = {}
    awsauth = AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, 'es')
    elasticsearch_kwargs.update(
        http_auth=awsauth,
        connection_class=elasticsearch.RequestsHttpConnection,
    )
    HAYSTACK_CONNECTIONS['default']['KWARGS'] = elasticsearch_kwargs

CACHES = {
    'default': env.cache_url('CACHE_URL', default='locmemcache://'),
}

SITE_ID = 1

handler404 = 'data_commons.views.page_not_found'
handler500 = 'data_commons.views.server_error'
#TODO 403 & 400

AUTH_USER_MODEL = 'profiles.User'

TAGGIT_CASE_INSENSITIVE = True

COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_MAX_THREAD_LEVEL = 2
COMMENTS_XTD_CONFIRM_EMAIL = False

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'stories.story': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    },
    'datasets.catalogrecord': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    },
}


ACCOUNT_ACTIVATION_DAYS = 7

RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
    }
}

if env.bool('TESTING', default=False):
    RQ_QUEUES['default']['ASYNC'] = False
    IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = 'imagekit.cachefiles.backends.Simple'

if not env('CACHE_URL', default=False): #no redis
    import sys
    sys.modules['django_rq'] = None
    INSTALLED_APPS.remove('django_rq')
    RQ_QUEUES['default']['ASYNC'] = False
    IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = 'imagekit.cachefiles.backends.Simple'

if env.bool('HAYSTACK_RT_UPDATES', default=True):
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
else:
    HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.BaseSignalProcessor'

#HAYSTACK_DJANGO_CT_FIELD = '_type'
#HAYSTACK_DJANGO_ID_FIELD = '_id'

#CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'extraPlugins': 'pastefromword',#'image2,pastefromword',
        #pastefromword
    },
}


ACTSTREAM_SETTINGS = {
    #'MANAGER': 'myapp.managers.MyActionManager',
    'FETCH_RELATIONS': True,
    'USE_JSONFIELD': True,
}

THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

CMS_TEMPLATES = (
    ('fullwidth.html', 'Fullwidth'),
    ('sidebar_left.html', 'Sidebar Left'),
    ('sidebar_right.html', 'Sidebar Right'),
    ('sidebars_left_right.html', 'Sidebars Left & Right'),
    ('priority_pages/priority_page.html', 'Priority Page'),
)


LANGUAGES = (
    ('en-us', 'en-us'),
)


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

DJANGOCMS_FORMS_RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default=None)
DJANGOCMS_FORMS_RECAPTCHA_SECRET_KEY = env('RECAPTCHA_SECRET_KEY', default=None)


COMMENTS_XTD_FORM_CLASS = 'data_commons.forms.CommentForm'
COMMENTS_XTD_MARKUP_FALLBACK_FILTER = 'markdown'


if env('AWS_STORAGE_BUCKET_NAME', default=None):
    DEFAULT_FILE_STORAGE = 'data_commons.contrib.storages.CustomS3Boto3Storage'
    #TODO this may go haywire with AWS_LOCATION usage
    #STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
    AWS_QUERYSTRING_AUTH = False

ENABLE_DEBUG_TOOLBAR = env.bool('ENABLE_DEBUG_TOOLBAR', default=False)
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(4, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    DEBUG_TOOLBAR_CONFIG = {
        'INTERNAL_IPS': ['127.0.0.1'],
        'SHOW_TOOLBAR_CALLBACK': 'data_commons.contrib.show_callback',
        'RENDER_PANELS': True, #because 404 shit happens
    }

ENABLE_DEV_EMAIL = env.bool('ENABLE_DEV_EMAIL', default=False)
if ENABLE_DEV_EMAIL:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = env('EMAIL_FILE_PATH', default='/code/var/app-messages')


EMAIL_HOST = env('EMAIL_HOST', default=False)
if EMAIL_HOST:
    EMAIL_USE_TLS = True #security is not an option
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)


MAILGUN_API_KEY = env('MAILGUN_API_KEY', default=False)
if MAILGUN_API_KEY:
    ANYMAIL = {
        "MAILGUN_API_KEY": MAILGUN_API_KEY
    }
    MAILGUN_SENDER_DOMAIN = env('MAILGUN_SENDER_DOMAIN', default=False)
    if MAILGUN_SENDER_DOMAIN:
        ANYMAIL['MAILGUN_SENDER_DOMAIN'] = MAILGUN_SENDER_DOMAIN
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"


DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default="donotreply@example.com")
REGISTRATION_SALT = env('REGISTRATION_SALT', default='registration')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

if PRODUCTION:
    LOGGING['loggers']['django.request'] = {
        'handlers': ['console', 'mail_admins'],
        'level': 'ERROR',
        'propagate': False,
    }

ADMINS = [('Jason', 'jkraus+scdclog@shift3tech.com')]

CMS_PLACEHOLDER_CONF = {
    'collapsible': {
        'plugins': ['CollapsiblePublisher']
    }
}

#only a good idea if we dont have allot of acronyms
#TAGGIT_CASE_INSENSITIVE = True

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
if SECURE_SSL_REDIRECT:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

if env('SECURE_HSTS_SECONDS', default=False):
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS')

if env('SECURE_PROXY_SSL_HEADER', default=False):
    SECURE_PROXY_SSL_HEADER = (env('SECURE_PROXY_SSL_HEADER'), 'https')
    MIDDLEWARE.insert(len(MIDDLEWARE)-2, 'data_commons.middleware.CacheVaryByProtocol')
