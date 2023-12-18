FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
COPY /requirements.txt /
RUN echo "nameserver 114.114.114.114" |  tee -a /etc/resolv.conf
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app  /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

