import os
import environ

env = environ.Env()
environ.Env.read_env()

from .common import *

DEBUG = False
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = []