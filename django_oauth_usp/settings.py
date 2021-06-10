import os
from pathlib import Path
from dj_database_url import parse as dburl

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


SECRET_KEY = 'alterar:my-secret-key'

AUTH_USER_MODEL = 'accounts.UserModel'

OAUTH_CALLBACK_ID = '4'

AUTHLIB_OAUTH_CLIENTS = {
    'usp': {
        'client_id': 'my_client_id',
        'client_secret': 'my_secret'
    }
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_oauth_usp.accounts'
]

ALLOWED_UNIDADES = [14]
REDIRECT_URI = '/user'
REDIRECT_AFTER_LOGOUT_URL = '/login'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_oauth_usp.accounts.middleware.OAuthUspMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': './db.sqlite3'
    }
}

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

ROOT_URLCONF = 'django_oauth_usp.urls'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'