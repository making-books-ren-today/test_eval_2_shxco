"""
Django settings for mep project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default debug to False, override locally
DEBUG = False

# Override in local settings, if using DEBUG = True locally, 'localhost'
# and variations allowed
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'django_cas_ng',
    'pucas',
    'dal',
    'dal_select2',
    'viapy',
    'mezzanine.boot',
    'mezzanine.conf',
    'mezzanine.core',
    'mezzanine.generic',
    'mezzanine.pages',
    # local apps
    'mep.common',
    'mep.people',
    'mep.accounts',
    'mep.books',
    'mep.footnotes',
]

MIDDLEWARE = [
    'mezzanine.core.middleware.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mezzanine.core.request.CurrentRequestMiddleware',
    'mezzanine.core.middleware.RedirectFallbackMiddleware',
    'mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware',
    # 'mezzanine.core.middleware.SitePermissionMiddleware',
    'mezzanine.pages.middleware.PageMiddleware',
    'mezzanine.core.middleware.FetchFromCacheMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

ROOT_URLCONF = 'mep.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates")
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mezzanine.conf.context_processors.settings',
                'mezzanine.pages.context_processors.page',
                'mep.context_extras',
                'mep.context_processors.template_settings',
            ],
            'builtins': [
                'mezzanine.template.loader_tags',
            ],
           'loaders': [
                'apptemplates.Loader',
                # 'mezzanine.template.loaders.host_themes.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

WSGI_APPLICATION = 'mep.wsgi.application'

GRAPPELLI_ADMIN_TITLE = 'MEP Admin'


# mezzanine integration package names (normally uses custom forks)
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli"


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
    "debug_toolbar",
    "django_extensions",
    "compressor",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

# override mezzanine version of jquery-ui with a more up-to-date version
JQUERY_UI_FILENAME = 'jquery-ui-1.12.1.min.js'

# pucas configuration that is not expected to change across deploys
# and does not reference local server configurations or fields
PUCAS_LDAP = {
    # basic user profile attributes
    'ATTRIBUTES': ['givenName', 'sn', 'mail'],
    'ATTRIBUTE_MAP': {
        'first_name': 'givenName',
        'last_name': 'sn',
        'email': 'mail',
    },
}

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'sitemedia'),
]

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1

# use mezzanine config to customize admin so that project-specific content
# is listed first - accounts, then people
ADMIN_MENU_ORDER = (
    ("Library Accounts", ("accounts.Account", "accounts.Event", "accounts.Subscription",
        "accounts.Reimbursement", "accounts.SubscriptionType")),
    ("Personography", ("people.Person", "people.Address", "people.Country",
        "people.Profession", "people.RelationshipType")),
    ("Bibliography", ("books.Item",)),
    ("Footnotes", ("footnotes.SourceType", "footnotes.Bibliography",
        "footnotes.Footnote")),
    ("Content", ("pages.Page", "generic.ThreadedComment",)),
    ("Site", ("sites.Site", "redirects.Redirect", "conf.Setting")),
)


##################
# LOCAL SETTINGS #
##################

# (local settings import logic adapted from mezzanine)

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

f = os.path.join(BASE_DIR, "mep", "local_settings.py")
if os.path.exists(f):
    import sys
    import imp
    module_name = "mep.local_settings"
    module = imp.new_module(module_name)
    module.__file__ = f
    sys.modules[module_name] = module
    exec(open(f, "rb").read())


## Mezzanine dynamic settings

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
