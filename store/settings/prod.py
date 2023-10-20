import os
import dj_database_url
import environ

env = environ.Env()
environ.Env.read_env()

from .common import *

DEBUG = False
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['grenatebuy-prod-ba2fdac05efc.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}

REDIS_URL = os.environ['REDIS_URL']

CELERY_BROKER_URL = REDIS_URL

EMAIL_HOST = os.environ['MAILGUN_SMTP_SERVER']
EMAIL_HOST_USER = os.environ['MAILGUN_SMTP_LOGIN']
EMAIL_HOST_PASSWORD = os.environ['MAILGUN_SMTP_PASSWORD']
EMAIL_PORT = os.environ['MAILGUN_SMTP_PORT']