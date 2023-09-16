## FastAPI练习测试

---
## 启动Celery的主服务
``` python
 celery -A app.Fast_blog.middleware.backlist worker --loglevel=info -P eventlet
 ```
---
## 启动Celery的调度器进行自动执行
``` python
 celery -A app.Fast_blog.middleware.celerybeat-schedule:celery_app beat
 ```
---

