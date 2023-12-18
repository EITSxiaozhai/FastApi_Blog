FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
COPY /requirements.txt /
RUN echo "nameserver 1.1.1.1" |  tee -a /etc/resolv.conf
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY ./app  /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

