#!/bin/bash
set -x
action=$1
shift

case $action in
  web-dev)
    exec python manage.py runserver 0.0.0.0:8001 --settings=sendcloud.settings
    ;;
  web-prod)
    exec uwsgi /app/uwsgi.ini "$@"
    ;;
  collectstatic)
    exec python manage.py collectstatic --noinput
    ;;
  celery_worker)
    exec celery -A sendcloud worker -l info "$@"
    ;;
  celery_beats)
    exec celery beat -A sendcloud -S django_celery_beat.schedulers.DatabaseScheduler -l INFO "$@"
    ;;
  *)
    exec $action "$@"
    ;;
esac
