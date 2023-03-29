# ----- coding: utf-8 ------
# author: YAO XU time:
from asyncio import Queue

from celery import Celery
from celery.schedules import crontab
from kombu import serialization
from kombu.serialization import register
import dill



register('dill', dill.dumps, dill.loads, content_type='application/x-python-serialize')
celery_app = Celery('tasks', broker='amqp://admin:005q8LzBwPaVA7Mb1AY9@106.14.159.61:5672//fastapi', backend='redis://:KsicwKTvK062ichw30Av@106.14.159.61:7000/3',task_serializer='dill', result_serializer='dill',
    accept_content=['json', 'dill'])



##创建每天12点自动执行
CELERY_BEAT_SCHEDULE = {
    'add-every-day': {
        'task': 'task.LetView',
        'schedule': crontab(),
    },
}
