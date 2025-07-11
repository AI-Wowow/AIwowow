"""
Django settings for video platform project.
"""
# Cloud SQL Python Connector patch
# This must be imported and called before any other Django imports.
try:
    from cloud_sql_python_connector.django.pre_settings import patch
    patch()
except ImportError:
    pass

import os
from pathlib import Path
from decouple import config
import sys

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps directory to Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.herokuapp.com', '.railway.app']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'storages',
    'drf_spectacular',
]

LOCAL_APPS = [
    'accounts',
    'videos',
    'evaluations',
    'core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}


# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Google Cloud Storage Settings
# These settings are used when USE_GCS is True.
USE_GCS = config('USE_GCS', default=False, cast=bool)

if USE_GCS:
    from storages.backends.gcloud import GoogleCloudStorage

    GS_BUCKET_NAME = config('GS_BUCKET_NAME')
    GS_SERVICE_ACCOUNT_NAME = config('GS_SERVICE_ACCOUNT_NAME', default=None)

    # Define separate storage classes for public static files and private media files.
    class StaticStorage(GoogleCloudStorage):
        def __init__(self, *args, **kwargs):
            kwargs['location'] = 'static'
            kwargs['default_acl'] = 'publicRead'
            super().__init__(*args, **kwargs)

    class MediaStorage(GoogleCloudStorage):
        def __init__(self, *args, **kwargs):
            kwargs['location'] = 'media'
            kwargs['querystring_auth'] = True
            kwargs['url_expiration'] = 3600  # 1 hour
            kwargs['service_account_name'] = GS_SERVICE_ACCOUNT_NAME
            super().__init__(*args, **kwargs)

    # Assign the custom storage classes
    STATICFILES_STORAGE = 'config.settings.StaticStorage'
    DEFAULT_FILE_STORAGE = 'config.settings.MediaStorage'

    # URLs
    STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
    
    STATIC_ROOT = "static/"
    MEDIA_ROOT = "media/"

else:
    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [BASE_DIR / 'static']

    # Media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
""

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Django Allauth settings
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Email settings
# Enhanced Email Configuration
if DEBUG:
    # For development, use console backend unless email is specifically configured
    if not config('EMAIL_HOST_USER', default=''):
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
        EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
        EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
        EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
        EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
        DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
else:
    # Production email settings
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Email verification settings
EMAIL_VERIFICATION_TOKEN_LIFETIME = 24  # hours
PASSWORD_RESET_TOKEN_LIFETIME = 2  # hours

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 500  # 500MB
MAX_FILE_SIZE = config('MAX_FILE_SIZE', default='524288000', cast=int)  # 500MB

# Video settings
ALLOWED_VIDEO_EXTENSIONS = config(
    'ALLOWED_VIDEO_EXTENSIONS', 
    default='mp4,mov,avi,webm,mkv'
).split(',')

# Development-specific settings
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Video Platform API',
    'DESCRIPTION': 'API for video submission and evaluation platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Authentication URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'
