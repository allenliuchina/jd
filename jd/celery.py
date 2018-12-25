from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jd.settings')
app = Celery('jd')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'index': {
        'task': 'good.tasks.generate_index_html',
        'schedule': 3600.0,
    },
    'page': {
        'task': 'good.tasks.create_page_cache',
        'schedule': 1800.0,
    },
    # 'new_good': {
    #     'task': 'good.tasks.create_new_good_cache',
    #     'schedule': 600.0
    # }

}
