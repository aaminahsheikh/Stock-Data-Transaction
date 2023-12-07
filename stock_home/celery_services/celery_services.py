from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockData.settings')


celery_app = Celery(
    'stock_home',
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=['stock_home.celery_services.celery_tasks.celery_tasks'],
    task_serializer='json',
    result_serializer='json',
    worker_send_task_events=True,
    task_send_sent_event=True
)

celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.conf.enable_utc = False
celery_app.conf.update(timezone="Asia/Karachi")

celery_app.autodiscover_tasks()

# celery_app.conf.beat_schedule = {
#     "check_video_status": {
#         "task": "check_video_status",
#         "schedule": 30, # seconds to schedule
#     },
# }
