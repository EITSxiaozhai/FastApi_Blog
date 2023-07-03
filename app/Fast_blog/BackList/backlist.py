# ----- coding: utf-8 ------
# author: YAO XU time:
import sys
from datetime import timedelta
from celery import Celery



celery_app = Celery('tasks',broker='amqp://admin:005q8LzBwPaVA7Mb1AY9@106.14.159.61:5672//fastapi', backend='redis://:KsicwKTvK062ichw30Av@106.14.159.61:7000/3')

#
@celery_app.task(name="BackList/backlist")
def add(x, y):
    return x + y





