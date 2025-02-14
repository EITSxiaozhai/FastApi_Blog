#!/bin/bash
# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
# 启动 Uvicorn 服务
exec uvicorn main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips "172.17.0.1"