# Fastapi + Vue3/2 的全栈项目

# 基本实现功能

---

## 普通用户端
* 查看文章功能
* 登录注册功能
* 评论区功能
* 打分公告
* Google验证码登录注册验证
* 文章博客实时传输到Redis中。减轻数据库压力。实现了Redis和Mysql同步功能

## 管理员功能

* 增删改查对应文章
* 使用了[vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)进行管理员端管理
* 审查评论
* 查看注册用户
* 发送重置密码邮件(暂未实现)
* 详细实现功能可以跳转到vue-element-admin上查看。
* Google验证码登录注册验证
* 双Token自动续期，全局管理员Token拦截。

## 中间件功能
* 全局Token验证拦截。必须携带token才能进行某些接口的访问。
* 日志格式化功能.接受来自uvicorn的日志。并且格式化成对应形式。通过ELK进行日志存储使用等
---


## 前提准备

- Mysql
- redis
- RabbitMQ或者其他消息队列代替
- Python3-Fastapi
- vue3和vue2的环境
- 阿里云的OSS key，用来存放文章首页图片
- Google 验证码的密钥，分为两个角色请分开。
- ELK的日志服务器地址
## 目录介绍
* app目录存储为
# 部署方法

---

## 0.部署前提

该项目目前存在的Python env配置.当然可以自己后续自行添加,如果你不知道什么是ENV请Google
```
- ACCESS_KEY_ID
- ACCESS_KEY_SECRET
- DB_HOSTNAME
- DB_NAME
- DB_PASSWORD
- DB_PORT
- DB_USERNAME
- RECAPTCHA_SECRET_KEY
- REDIS_DB_HOSTNAME
- REDIS_DB_NAME
- REDIS_DB_PASSWORD
- REDIS_DB_PORT
- MQ_USERNAME
- MQ_USERPASSWORD
- MQ_HOSTNAME
- MQ_DBNAME
- MQ_DBPORT
- MQ_USERNAME
```
# 程序目录介绍

- [app](app)
  - [Fast_blog](/app/Fast_blog) 
    - [database](/app/Fast_blog/database) 数据库链接
    - [middleware](/app/Fast_blog/middleware) 中间件模块
    - [model](/app/Fast_blog/model) 数据库模型模块
    - [schemas](/app/Fast_blog/schemas) 请求验证模块
    - [unit](/app/Fast_blog/unit) app模块文件夹
      - [AdminAPP](/app/Fast_blog/unit/AdminApp) 管理员接口
      - [Blog_app](/app/Fast_blog/unit/Blog_app) 博客接口
      - [Power_crawl](/app/Fast_blog/unit/Power_Crawl) 爬虫接口（自用。可以删除）
      - [SystemMonitoring](/app/Fast_blog/unit/SystemMonitoring) websocket系统监控模块
      - [User_app](/app/Fast_blog/unit/User_app) 普通用户接口
        

---

## 1.手动部署  

### 后端部署方法

####  可以利用python直接运行后端接口

```
uvicorn.exe main:app --reload
```

后端启动完成后。代码中包含了自动启动邮件发送定时任务。当然你可以拆除它。并使用下面的命令进行手动启动

#### 启动Celery的主服务
``` python
 celery -A app.Fast_blog.middleware.backlist worker --loglevel=info -P eventlet
```
#### 启动Celery的循环定时任务调度器进行自动执行
``` python
 celery -A app.Fast_blog.middleware.celerybeat-schedule:celery_app beat
```
---

## 前端部署
#### 前端测试启动方法--部署到生产环境不安全。仅供功能测试
前端分为用户前端和管理前端。需要分别CD到对应的文件夹中随后开启web。
```
npm run dev
```
#### 前端生产环境部署方法

请参阅  [Deploy a Vite 3 site](https://developers.cloudflare.com/pages/framework-guides/deploy-a-vite3-project/)

---
## 其他提示

#### 后端接口地址

```
http://192.168.0.150:49200/docs
```

#### 用户前端接口地址

```
http://127.0.0.1:49300/
```

#### 管理员端地址

```
http://127.0.0.1:49400/
```

**注意此处会遇到跨域问题。如果在本机上开发就不需要担心这个问题。如果需要搭建到公网上去且安装SSL证书。参考nginx反向代理配置文件**

---
# Gitlab自动部署
在文件目录中存在了对应了.gitlab-ci.yml文件。该文件利用流水线发布。包含测试，打包，部署，可以自行修改。后端前端都存在了对应的Dockerfile，可以进行自动修改，你只需要将这个项目推送到存在这gitlab-runner仓库中。部署完成即可