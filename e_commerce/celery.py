import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce.settings')

app = Celery('e_commerce')

# Using a string here means the worker doesn't
# have to serialize the configuration object to
# child processes. - namespace='CELERY' means all
# celery-related configuration keys should
# have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# celery beat settings
app.conf.beat_schedule = {
    'cart_abundance_mail': {
        'task': 'shop.celery.tasks.send_cart_abundance_mail',
        'schedule': crontab(),
    }
}

# load task from all the apps
app.autodiscover_tasks()
