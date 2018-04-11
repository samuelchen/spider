"""
Django settings for novelreader project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.utils.functional import lazystr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_@ddb!r_bc5*x@*z=oi(a2p1jbbb_^vtt3^chv@u=m3sfl(7$s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # for django-allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.weibo',
    'allauth.socialaccount.providers.weixin',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'novelreader.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'novelreader', 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'novelreader.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'novelreader.sqlite3'),
    }
}


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

# for all auth
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)



# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/s/'
MEDIA_URL = '/m/'


# -------- allauth settings --------
SITE_ID = 1

ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'weibo', 'wechat', 'root', 'staff', 'contact',
                              'notification', 'administrator', 'manager', 'sale', 'billing', 'support'
                              'subscription', 'system', 'bill', 'account', 'service']

SOCIALACCOUNT_AUTO_SIGNUP = False

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = "mandatory"     # "mandatory", "optional", or "none"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'


# -------- added settings --------

WEBSITE = {
    'name': '壁虎看书',
    'short_name': '壁虎',
    'domain': 'bihu.com',
    'mobile_url': 'http://m.bihu.com'
}

# include all novels even has not started to download
ALL_NOVELS = os.environ.get('ALL_NOVELS', False)

# default items per page
ITEMS_PER_PAGE = 30

# NOVEL_DB_CONNECTION_STRING will be used in SqlAlchemy to query novels.
# http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
# format: driver://user:pass@host:port/database
NOVEL_DB_CONNECTION_STRING = 'sqlite:///' + os.path.join(BASE_DIR, 'novel.sqlite3')


MEDIA_ROOT = os.path.join(BASE_DIR, 'data/media')
STATIC_ROOT = os.path.join(BASE_DIR, 'data/static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)-8s [%(asctime)s] [%(process)-6d] [%(threadName)-8s] %(name)-30s [%(lineno)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)-8s [%(asctime)s] %(name)-30s [%(lineno)d] %(message)s'
        },
        'colored': {
            'format': '%(levelname)-8s [%(asctime)s] %(name)s.%(funcName)s [%(lineno)d] %(message)s',
            # color reference: https://pypi.python.org/pypi/termcolor
            # 'LEVEL': ('fg-color', 'bg-color', ['attr1', 'attr2', ...])
            # '()': 'pyutils.logger.ColorFormatter',
            'colors': {
                'TRACE': ('grey', None, []),
                'DEBUG': ('grey', None, ['bold']),
                'INFO': (None, None, []),
                'WARNING': ('yellow', None, []),
                'ERROR': ('red', None, []),
                'CRITICAL': ('red', 'white', []),

            }
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'novelreader': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}



