import sys
from datetime import timedelta
from backlist import celery_app



celery_app.conf.beat_schedule = {
    'every-second': {
        'task': 'BackList/backlist',  # 任务名称（指定任务的导入路径）
        'schedule': timedelta(seconds=1),  # 每秒执行一次
        'args': (16, 16),
    }
}