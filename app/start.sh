#!/bin/bash
# Run migrations
alembic upgrade head
# 启动 Uvicorn 服务
exec uvicorn main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips "*" --no-access-log