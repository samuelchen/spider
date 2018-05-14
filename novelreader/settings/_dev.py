from ._base import *

# -----------------------------
# Override base settings here
# -----------------------------


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['azure', 'localhost', '127.0.0.1']

INSTALLED_APPS.extend([
    # for django-allauth
    'allauth.socialaccount.providers.weibo',
    'allauth.socialaccount.providers.weixin',
])

MEDIA_ROOT = os.path.join(BASE_DIR, 'data/media')
STATIC_ROOT = os.path.join(BASE_DIR, 'data/static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    ('albums', os.path.abspath(os.path.join(BASE_DIR, '..', 'novelspider', 'albums'))),
]

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'data', 'email')


NOVEL_DB_CONNECTION_STRING = 'postgresql://postgres:postgres@localhost/novel'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'novelreader.sqlite3'),
    }
}

LOGGING.update({
    'loggers': {
        'novelreader': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
})


