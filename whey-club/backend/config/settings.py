import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'local-development-only-change-before-production')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
if not DEBUG and SECRET_KEY == 'local-development-only-change-before-production':
    raise RuntimeError('Set DJANGO_SECRET_KEY before production deployment')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.humanize', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.contenttypes', 'django.contrib.auth', 'django.contrib.sessions', 'store']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'store.middleware.SecureAccountMiddleware', 'django.middleware.common.CommonMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.csrf.CsrfViewMiddleware']
ROOT_URLCONF = 'config.urls'
# PostgreSQL is the default. SQLite is an explicit development/rollback option only.
DB_ENGINE = os.environ.get('WHEY_DB_ENGINE', 'postgresql')
if DB_ENGINE not in ('postgresql', 'sqlite'):
    raise ValueError('WHEY_DB_ENGINE must be postgresql or sqlite')
if DB_ENGINE == 'sqlite':
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.environ.get('WHEY_DATABASE', BASE_DIR / 'db.sqlite3')}}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'wheyclub'),
        'USER': os.environ.get('PGUSER', 'wheyclub'),
        'PASSWORD': os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('PGHOST', '127.0.0.1'),
        'PORT': os.environ.get('PGPORT', '5432'),
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {'connect_timeout': 10, 'sslmode': os.environ.get('PGSSLMODE', 'prefer')},
    }}

USE_TZ = True
TIME_ZONE = 'UTC'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CONTENT_DIR = Path(os.environ.get('WHEY_CONTENT_DIR', BASE_DIR.parent / 'content'))
PUBLICATION_STATE = Path(os.environ.get('WHEY_PUBLICATION_STATE', BASE_DIR.parent / '.publication-state/publication.json'))

AUTH_PASSWORD_VALIDATORS = [
 {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},
 {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
 {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
]
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG or os.environ.get('WHEY_HTTPS','0') == '1'
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
DATA_UPLOAD_MAX_MEMORY_SIZE = 65536

ACCOUNT_REQUIRE_HTTPS = os.environ.get('WHEY_REQUIRE_HTTPS','0' if DEBUG else '1') == '1'

LANGUAGE_CODE = 'fa'

CSRF_TRUSTED_ORIGINS = [x for x in os.environ.get('WHEY_CSRF_ORIGINS','http://localhost:5174,http://127.0.0.1:5174' if DEBUG else '').split(',') if x]

TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
STATIC_URL = '/django-static/'
STATIC_ROOT = os.environ.get('WHEY_STATIC_ROOT', BASE_DIR / 'staticfiles')
# The Django port is private; Nginx overwrites this header on every proxied request.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')

FRONTEND_ROOT = Path(os.environ.get('WHEY_FRONTEND_ROOT', BASE_DIR.parent / 'frontend/build'))
