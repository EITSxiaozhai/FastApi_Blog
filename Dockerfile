FROM docker.1ms.run/tiangolo/uvicorn-gunicorn-fastapi:python3.11
COPY /requirements.txt /
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app  /app
WORKDIR /app
# 不在构建期写入数据库 URL，运行时通过环境变量注入（见 app/alembic/env.py）
CMD ["/start.sh"]