# Use this settings file for development
from .base import *


SECRET_KEY = 'NOT_THE_SAME_AS_PRODUCTION'

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ROOT_URLCONF = 'webapp.urls.dev'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGIN_REDIRECT_URL = '/'
