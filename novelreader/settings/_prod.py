from ._base import *

# -----------------------------
# Override base settings here
# -----------------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_@ddb>,d7*bc5*x@*z=oi(a2pLdu92b_^vtt3^chv@u=m3sfl(7$s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.domain.com', 'domain.com', 'azure']

INSTALLED_APPS.extend([
    'novelreader',
])

MEDIA_ROOT = os.path.abspath('/opt/novelreader/media')
STATIC_ROOT = os.path.abspath('/opt/novelreader/static')

# to access novel database
NOVEL_DB_CONNECTION_STRING = 'postgresql://postgres:postgres@localhost/novel'

# to access reader database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': os.path.join(BASE_DIR, 'novelreader.sqlite3'),
    }
}


CACHES = {
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    #     'TIMEOUT': 600,     # seconds
    #     'OPTIONS': {
    #         'MAX_ENTRIES': 1000
    #     }
    # },
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.abspath(os.path.join(MEDIA_ROOT, 'cache')),
        'TIMEOUT': 3600,     # seconds
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    },
    # # python manage.py createcachetable
    # 'db': {
    #     'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    #     'LOCATION': 'weinsta_cache',
    # },
    # 'memcache': {
    #     'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #     'LOCATION': [
    #         '172.19.26.240:11211',
    #         '172.19.26.242:11212',
    #         '172.19.26.244:11213',
    #     ]
    # }
}
MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')
CACHE_MIDDLEWARE_SECONDS = 3600