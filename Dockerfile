FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
COPY /requirements.txt /
ARG Sql_URL
RUN python -m pip install --upgrade pip
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app  /app
WORKDIR /app
CMD sed -i "s|^sqlalchemy.url.*$|sqlalchemy.url = ${SQL_URL}|g" /app/alembic.ini
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80","--proxy-headers","--forwarded-allow-ips", "172.17.0.1"]

