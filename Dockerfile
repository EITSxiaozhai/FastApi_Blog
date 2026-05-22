FROM  tiangolo/uvicorn-gunicorn-fastapi:python3.11
COPY pyproject.toml uv.lock /tmp/fastapi-blog/
WORKDIR /tmp/fastapi-blog
RUN python -m pip install --no-cache-dir --upgrade uv
ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --frozen --no-cache --no-dev --no-install-project
COPY ./app  /app
WORKDIR /app
# 不在构建期写入数据库 URL，运行时通过环境变量注入（见 app/alembic/env.py）
CMD ["/start.sh"]
