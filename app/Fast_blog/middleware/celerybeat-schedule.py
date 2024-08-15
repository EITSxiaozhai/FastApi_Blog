from datetime import timedelta

from Fast_blog.middleware import celery_app

celery_app.autodiscover_tasks(['Fast_blog.unit.Blog_app'])

celery_app.conf.beat_schedule = {
    'update-redis-cache-every-24-hours': {
        'task': 'update_redis_cache',
        'schedule': timedelta(hours=24),  # 每24小时执行一次
    },
}