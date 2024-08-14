from datetime import timedelta

from celery.schedules import crontab

from .backtasks import celery_app


celery_app.autodiscover_tasks(['Fast_blog.unit.Blog_app'])

# celery_app.conf.beat_schedule = {
#     'every-second': {
#         'task': 'middleware/backtasks',  # 任务名称（指定任务的导入路径）
#         'schedule': timedelta(seconds=1),  # 每秒执行一次
#         'args': ("eitsxiaozhai@gmail.com",)
#     }
# }

# 定时任务调度
celery_app.conf.beat_schedule = {
    'update-redis-cache-every-24-hours': {
        'task': 'BlogAuto',
        'schedule': timedelta(seconds=3),  # 每3秒执行一次
    },
}