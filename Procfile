web: bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT crisix/settings.py
worker: bin/python crisix/manage.py celeryd -E -B --loglevel=INFO
