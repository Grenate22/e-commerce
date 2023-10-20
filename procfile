release: python manage.py migrate
web: gunicorn store.wsgi
worker: celery -A store worker