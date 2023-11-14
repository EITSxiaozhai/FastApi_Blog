# Fastapi + Vue3/2 的练习项目

## 该项目并没有完全完成。只有基础功能可以使用

## 前提准备

- Mysql
- redis
- RabbitMQ或者其他消息队列代替
- python3
- vue3和vue2的环境
- 阿里云的OSS key。Google it

# 部署方法

### **alembic导入数据库**。请参考下述教程。请先完成数据库迁移

https://juejin.cn/post/7077022949374443533

该项目使用了Gitlab进行自动部署。所以如果你想自己部署。请设置自己的环境配置文件。**请Google python env文件和VUe的env文件配置**。此步非常重要。否则无法启动。

该项目目前存在的Python env配置.当然可以自己后续自行添加

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

### 1.直接部署

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
### 下述为部署到公网或者服务器端的地址。如果再本机开发则不需要关心这个。以env配置文件为准
#### 前端启动方法

前端分为用户前端和管理前端。需要分别CD到对应的文件夹中随后开启web。

```
npm run dev
```



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

注意此处会遇到跨域问题。如果在本机上开发就不需要担心这个问题。如果需要搭建到公网上去且安装SSL证书。需要参考下面的nginx反向代理配置文件

### nginx反向代理例子

```nginx
cat vue-admin.conf 
server{

      listen *:15009 ssl http2;
  listen [::]:15009 ssl http2;
    server_name  xxxxx.com;
  ssl_stapling on;
  resolver 8.8.8.8 8.8.4.4 223.5.5.5 valid=300s;
  resolver_timeout 5s;
  ssl_certificate full_chain_rsa.crt;
  ssl_certificate_key key.key;
  ssl_client_certificate  /home/exploit/SSL/CA.crt;    
  ssl_protocols  TLSv1.1 TLSv1.2 TLSv1.3;

     location /admin  {
        proxy_pass http://127.0.0.1:49400/;
        proxy_cache_bypass $http_upgrade;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:49200;
        proxy_cache_bypass $http_upgrade;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

       location /static/ {
        proxy_pass http://192.168.0.150:49400/static/;
    }

    location /assets/ {
        proxy_pass http://192.168.0.150:49400/assets/;
    }

    location /static/js/ {
        proxy_pass http://192.168.0.150:49400/static/js/;  # Vue.js编译后的静态js文件路径
    }
}
```

### 后端接口和用户前端nginx配置文件例子

```nginx
cat fast_api.conf 
server{

      listen *:15008 ssl http2;
  listen [::]:15008 ssl http2;
    server_name  xxx.com;
  ssl_stapling on;
  resolver 8.8.8.8 8.8.4.4 223.5.5.5 valid=300s;
  resolver_timeout 5s;
  ssl_certificate full_chain_rsa.crt;
  ssl_certificate_key com.key;
  ssl_client_certificate  /home/exploit/SSL/CA.crt;    
 ssl_protocols  TLSv1.1 TLSv1.2 TLSv1.3;



     location /blog {
        proxy_pass http://127.0.0.1:49300/;
        proxy_cache_bypass $http_upgrade;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    location /api {
        proxy_pass http://127.0.0.1:49200;
        proxy_cache_bypass $http_upgrade;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Script-Name /api;
    }

       location /static/ {
        proxy_pass http://192.168.0.150:49300/static/;
    }

    location /assets/ {
        proxy_pass http://192.168.0.150:49300/assets/;
    }

    location /static/js/ {
        proxy_pass http://192.168.0.150:49300/static/js/;  # Vue.js编译后的静态js文件路径
    }
}
```

### 2. 利用Gitlab自动部署到环境

将代码拉取到自己的Gitlab中后。他会自动利用docker部署。CI/CD。非常方便。后续更新只需要push你自己的代码。服务器端自动完成更新。前提是服务器端安装了docker和在gitlab中进行了agent安装。

### 利用gitlab部署完成后。还是需要利用nginx进行反向代理

**请参考上述示例代码**
