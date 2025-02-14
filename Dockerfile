FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
COPY /requirements.txt /
ARG Sql_URL
RUN python -m pip install --upgrade pip
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app  /app
WORKDIR /app
RUN sed -i "s|^sqlalchemy.url.*$|sqlalchemy.url = ${Sql_URL}|g" /app/alembic.ini
CMD ["/start.sh"]

