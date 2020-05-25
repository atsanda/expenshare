# Use this settings file for development
from .base import *


SECRET_KEY = 'NOT_THE_SAME_AS_PRODUCTION'

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ROOT_URLCONF = 'webapp.urls.dev'