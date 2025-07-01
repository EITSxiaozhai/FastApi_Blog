# 🚀 FastAPI + Vue 全栈博客系统

一个现代化的全栈博客平台，采用 FastAPI + Vue3/2 技术栈，集成了丰富的功能模块和现代化的开发实践。

## ✨ 核心特性

### 🔐 认证与安全
- **多重认证机制**：JWT 双 Token 自动续期（访问 Token + 刷新 Token）
- **第三方登录**：GitHub OAuth 2.0 集成，支持二维码扫码登录
- **会话管理**：Redis + 内存双层缓存会话存储
- **Google reCAPTCHA**：管理员和普通用户分离式验证
- **邮箱验证**：用户注册邮箱验证机制
- **权限管理**：基于角色的访问控制（RBAC）

### 📝 博客核心功能
- **文章管理**：支持 Markdown 编辑，富文本内容
- **智能缓存**：Redis 缓存系统，自动同步数据库变更，支持缓存预热
- **标签系统**：文章分类标签管理
- **评分系统**：5 星评分，防重复投票机制
- **评论系统**：支持嵌套回复的树形评论结构
- **全文搜索**：文章标题和内容搜索
- **SEO 优化**：自动提交到 Google/Bing 搜索引擎
- **分页优化**：高效的分页查询机制

### 📊 数据分析与监控
- **实时监控**：WebSocket 实时系统性能监控（CPU/内存）
- **访问统计**：集成 Google Analytics，实时 UV/PV 统计
- **日志管理**：结构化日志，支持 ELK 日志分析

### 🔧 技术亮点
- **异步架构**：全异步 FastAPI + SQLAlchemy 异步 ORM
- **消息队列**：Celery + RabbitMQ 异步任务处理
- **文件存储**：阿里云 OSS 对象存储集成
- **数据库**：MySQL + Redis 双存储架构
- **容器化**：Docker + GitLab CI/CD 自动化部署
- **缓存策略**：多级缓存架构，支持缓存预热和自动失效
- **连接池**：数据库和 Redis 连接池优化
- **安全机制**：防 SQL 注入、XSS 攻击、CSRF 防护

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户前端      │    │   管理员前端    │    │   移动端 H5     │
│   (Vue3/Vike)   │    │ (Vue Element)   │    │   (响应式)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      FastAPI 后端        │
                    │   (异步 API Gateway)     │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │   MySQL   │         │   Redis   │         │    OSS    │
    │  主数据库  │         │   缓存层   │         │  文件存储  │
    └───────────┘         └───────────┘         └───────────┘
```

## 📁 项目结构

```
FastApi_Blog/
├── app/                          # 后端应用
│   ├── Fast_blog/
│   │   ├── database/            # 数据库连接层
│   │   ├── middleware/          # 中间件模块
│   │   │   ├── backtasks.py     # Celery 异步任务
│   │   │   └── TokenAuthentication.py # JWT 认证
│   │   ├── model/               # 数据模型层
│   │   ├── schemas/             # 请求/响应模型
│   │   └── unit/                # 业务模块
│   │       ├── AdminApp/        # 管理员接口
│   │       ├── Blog_app/        # 博客核心接口
│   │       ├── User_app/        # 用户管理接口
│   │       ├── SystemMonitoring/# 系统监控 WebSocket
│   │       └── Power_Crawl/     # 数据爬虫模块
│   └── main.py                  # 应用入口
├── blogvuets/                   # 用户前端 (Vue3 + Vike)
└── vue-element-admin-master/    # 管理后台 (Vue2 + Element)
```

## 🛠️ 技术栈

### 后端技术
- **Web 框架**：FastAPI (异步高性能)
- **ORM**：SQLAlchemy 2.0 (异步)
- **数据库**：MySQL 8.0+ / Redis 6.0+
- **任务队列**：Celery + RabbitMQ
- **认证**：JWT + OAuth2
- **文件存储**：阿里云 OSS
- **日志**：Logstash + ELK Stack

### 前端技术
- **用户端**：Vue 3 + Vike (SSR)
- **管理端**：Vue 2 + Element UI
- **状态管理**：Pinia / Vuex
- **HTTP 客户端**：Axios
- **UI 组件**：Element Plus / Element UI

### DevOps
- **容器化**：Docker + Docker Compose
- **CI/CD**：GitLab Runner
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+
- RabbitMQ 3.8+

### 环境变量配置
创建 `.env` 文件并配置以下变量：

```bash
# 数据库配置
DB_HOSTNAME=localhost
DB_PORT=3306
DB_NAME=blog_db
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Redis 配置
REDIS_DB_HOSTNAME=localhost
REDIS_DB_PORT=6379
REDIS_DB_PASSWORD=your_redis_password
REDIS_DB_NAME=0

# 消息队列配置
MQ_HOSTNAME=localhost
MQ_DBPORT=5672
MQ_USERNAME=your_mq_username
MQ_USERPASSWORD=your_mq_password
MQ_DBNAME=your_vhost

# 阿里云 OSS 配置
ACCESS_KEY_ID=your_access_key_id
ACCESS_KEY_SECRET=your_access_key_secret

# Google 服务配置
ADMIN_RECAPTCHA_SECRET_KEY=your_admin_recaptcha_key
GENERAL_USER_RECAPTCHA_SECRET_KEY=your_user_recaptcha_key

# JWT 配置
SECRET_KEY=your_jwt_secret_key
REFSECRET_KEY=your_refresh_secret_key

# GitHub OAuth 配置
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
REDIRECT_URI=your_redirect_uri

# SMTP 邮件配置
SMTPSERVER=your_smtp_server
SMTPPORT=587
SMTPUSER=your_email
SMTPPASSWORD=your_email_password

# ELK 日志配置
LOGSTASH_NGINX_HOST=your_logstash_host
LOGSTASH_NGINX_PORT=443
LOGSTASH_USER=your_logstash_user
LOGSTASH_PASS=your_logstash_password
```

### 🐳 Docker 部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd FastApi_Blog

# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 📦 手动部署

#### 后端部署
```bash
# 进入后端目录
cd app

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动 Celery Worker (新终端)
celery -A Fast_blog.middleware.backtasks:celery_app worker --loglevel=info -P eventlet

# 启动 Celery Beat (新终端)
celery -A Fast_blog.middleware.backtasks:celery_app beat --loglevel=info
```

#### 前端部署
```bash
# 用户前端
cd blogvuets
npm install
npm run dev  # 开发模式
npm run build  # 生产构建

# 管理后台
cd vue-element-admin-master
npm install
npm run dev  # 开发模式
npm run build:prod  # 生产构建
```

## 🌐 访问地址

- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **用户前端**：http://localhost:3000
- **管理后台**：http://localhost:9527

## 🔌 API 接口概览

### 用户端接口 (`/api/generaluser`)
- 用户注册/登录
- 邮箱验证
- GitHub OAuth 登录
- 评论管理
- 用户资料更新

### 博客接口 (`/api/views`)
- 文章列表分页查询
- 文章详情获取
- 文章搜索
- 文章评分
- Bing 每日壁纸

### 管理员接口 (`/api/admin`)
- 管理员认证
- 用户管理 CRUD
- 文章管理 CRUD
- 标签管理
- SEO 优化工具

### 系统监控 (`/api/monitoring`)
- WebSocket 实时监控
- 系统性能数据

## ⚠️ 部署注意事项

### 生产环境配置
1. **HTTPS 证书**：建议使用 Let's Encrypt 或其他 SSL 证书
2. **Nginx 反向代理**：配置负载均衡和静态文件服务
3. **数据库优化**：MySQL 索引优化，Redis 内存配置
4. **安全配置**：防火墙设置，端口限制
5. **监控告警**：配置系统监控和日志告警

### 性能优化建议
- 启用 Redis 缓存预热
- 配置 CDN 加速静态资源
- 数据库读写分离
- 启用 Gzip 压缩

## 📋 主要功能模块

### 👤 用户系统
- [x] 用户注册/登录
- [x] 邮箱验证
- [x] GitHub OAuth 登录
- [x] 二维码扫码登录
- [x] 用户资料管理
- [x] 头像上传

### 📖 博客系统
- [x] 文章 CRUD 操作
- [x] Markdown 编辑器
- [x] 图片上传
- [x] 文章分类标签
- [x] 文章搜索
- [x] 文章缓存优化
- [x] Bing 每日壁纸集成
- [x] 文章发布状态管理
- [x] 文章访问量统计

### 💬 互动功能
- [x] 文章评论系统
- [x] 嵌套回复
- [x] 文章评分
- [x] 点赞功能

### 🔧 管理后台
- [x] 用户管理
- [x] 权限管理
- [x] 文章管理
- [x] 评论审核
- [x] 系统监控
- [x] SEO 管理（Google/Bing 搜索引擎提交）
- [x] 文件上传管理
- [x] 动态权限菜单

### 📊 数据统计
- [x] 访问统计 (UV/PV)
- [x] 系统性能监控
- [x] 日志分析
- [x] 电力数据爬虫（可选模块）

## 🔄 CI/CD 流水线

项目支持 GitLab CI/CD 自动化部署：

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pytest

build:
  stage: build
  script:
    - docker build -t blog-api .

deploy:
  stage: deploy
  script:
    - docker-compose up -d
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element UI](https://element.eleme.io/) - 基于 Vue 2.0 的桌面端组件库
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues](link-to-issues)
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！