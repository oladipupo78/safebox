from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safebox.settings')
app = Celery('safebox')
app.conf.enable_utc = False
app.conf.update(timezone = 'UTC')
app.config_from_object(settings,namespace='CELERY')

# CELERY BEAT SETTINGS
app.conf.beat_schedule = {
    'print 1-10 & print 10':{
        'task': 'accounts.tasks.test_func',
        'schedule': crontab(hour=0, minute=46)
    }
}

app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
