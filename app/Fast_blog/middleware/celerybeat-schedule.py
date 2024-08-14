from datetime import timedelta

from celery.schedules import crontab

from .backtasks import celery_app

# Schedule the task every 24 hours
celery_app.conf.beat_schedule = {
    'update-redis-cache-every-24-hours': {
        'task': 'tasks.update_redis_cache',
        'schedule': crontab(hour=0, minute=0),  # Every 24 hours
    },
}
