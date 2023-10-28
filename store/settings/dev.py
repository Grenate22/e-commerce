from .common import *

DEBUG = True
SECRET_KEY = 'django-insecure-j^3mgrc!l-x4krylm$q5fhc06_tp8zvaez%&x=z)mx%-e2#i!w'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Ladenposse3'
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = 'info@grnate.com'