import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config', include=['users.tasks', ])
app.config_from_object('django.conf.settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()
app.conf.broker_transport_options = {'max_retries': 5}

app.conf.beat_schedule = {
    'celery_vocations': {
        'task': 'users.tasks.chek_vocations',
        'schedule': crontab(minute=1, hour=0),
    },
}
