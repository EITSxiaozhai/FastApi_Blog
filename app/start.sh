#!/bin/bash
set -e  # 如果任何命令失败，则退出脚本

# 执行数据库迁移
alembic upgrade head

# 启动 Uvicorn 服务
exec uvicorn main:app --host 0.0.0.0 --port 80 --proxy-headers --forwarded-allow-ips "172.17.0.1"