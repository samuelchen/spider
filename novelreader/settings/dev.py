from ._base import *

# -----------------------------
# Override base settings here
# -----------------------------


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS.extend([
    'novelreader',
])

MEDIA_ROOT = os.path.join(BASE_DIR, 'data/media')
STATIC_ROOT = os.path.join(BASE_DIR, 'data/static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    ('albums', os.path.abspath(os.path.join(BASE_DIR, '..', 'novelspider', 'albums'))),
]

NOVEL_DB_CONNECTION_STRING = 'postgresql://postgres:postgres@192.168.0.93/novel'
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


