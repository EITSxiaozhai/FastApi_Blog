# Fastapi + Vue3/2 的全栈练习项目

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

---


## 前提准备

- Mysql
- redis
- RabbitMQ或者其他消息队列代替
- Python3-Fastapi
- vue3和vue2的环境
- 阿里云的OSS key。用来存放文章首页图片


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

---

## 1.手动部署  

### 后端部署方法

####  可以利用python直接运行后端接口

```
uvicorn.exe main:app --reload
```

后端启动完成后。可以随你个人想法是否启动消息队列。准备添加后台自定义任务。但是还没有实现

#### 启动Celery的主服务
``` python
 celery -A app.Fast_blog.middleware.backlist worker --loglevel=info -P eventlet
```
#### 启动Celery的调度器进行自动执行
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
