import os
from celery import Celery
from celery.schedules import crontab

from app.config.settings import get_settings

settings = get_settings()

celery = Celery(
    "nutriform",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)
celery.conf.timezone = settings.celery_timezone
CELERY_BEAT_SCHEDULE = {
    'some-task': {
        'task': 'app.tasks.some_task',
        'schedule': crontab(minute=0, hour='*/1'),  # ✔️ Используем crontab объект
        'args': (),
    }
}