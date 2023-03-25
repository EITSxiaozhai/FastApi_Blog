## FastAPI练习测试


075a5056de19451dae9aff7a815dc1da  

---

## Nextcloud使用Nginx进行搭建  

###
```
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
        worker_connections 4096;
        #       worker_processes auto;
        # multi_accept on;
}

http {
       include       /etc/nginx/sites-enabled/nextcloud.conf; 
       include       /etc/nginx/sites-enabled/gitlab.conf;
       include       /etc/nginx/sites-enabled/Fast_api.conf;
        ##
        # Basic Settings
        ##
        # add_header Strict-Transport-Security max-age=15552000;
        sendfile on;
        tcp_nopush on;
        types_hash_max_size 2048;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;
        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings
        ##

        gzip on;

        # gzip_vary on;
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k;
        # gzip_http_version 1.1;
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        ##
        # Virtual Host Configs
        ##
        client_max_body_size 30000M;
        include /etc/nginx/conf.d/*.conf;
#       include /etc/nginx/sites-enabled/*;
}


#mail {
#       # See sample authentication script at:
#       # http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
#
#       # auth_http localhost/auth.php;
#       # pop3_capabilities "TOP" "USER";
#       # imap_capabilities "IMAP4rev1" "UIDPLUS";
#
#       server {
#               listen     localhost:110;
#               protocol   pop3;
#               proxy      on;
#       }
#
#       server {
#               listen     localhost:143;
#               protocol   imap;
#               proxy      on;
#       }
#}
```  
### 文件夹权限配置  
```
chown -R www-data:www-data /var/www/nextcloud
chmod -R 755 /var/www/nextcloud
```  
### Nginx转发配置
```
upstream php-handler {
    #server 127.0.0.1:9000;
    server unix:/var/run/php/php7.4-fpm.sock;
}

# Set the `immutable` cache control options only for assets with a cache busting `v` argument
map $arg_v $asset_immutable {
    "" "";
    default "immutable";
}


server {
    listen 81;
    listen [::]:81;
    server_name cloud.example.com;

    # Prevent nginx HTTP Server Detection
    server_tokens off;

    # Enforce HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 15006      ssl http2;
    listen [::]:15006 ssl http2;
    server_name www.exploit-db.xyz;

    # Path to the root of your installation
    root /etc/nginx/html/nextcloud;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 223.5.5.5 valid=300s;
    resolver_timeout 5s;
    # Use Mozilla's guidelines for SSL/TLS settings
    # https://mozilla.github.io/server-side-tls/ssl-config-generator/
    ssl_certificate /home/exploit/SSL/zhengshu.csr; # 你的SSL证书crt文件
    ssl_certificate_key /home/exploit/SSL/exploit-db.xyz.key;# 你的SSL证书key文件
    ssl_client_certificate  /home/exploit/SSL/CA.crt;
     ssl_trusted_certificate  /home/exploit/SSL/zhengshu.csr;
        # Prevent nginx HTTP Server Detection
    server_tokens off;

    # HSTS settings
    # WARNING: Only add the preload option once you read about
    # the consequences in https://hstspreload.org/. This option
    # will add the domain to a hardcoded list that is shipped
    # in all major browsers and getting removed from this list
    # could take several months.
    add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload" always;

    # set max upload size and increase upload timeout:
    client_max_body_size 512M;
    client_body_timeout 300s;
    fastcgi_buffers 64 4K;

    # Enable gzip but do not remove ETag headers
    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/wasm application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    # Pagespeed is not supported by Nextcloud, so if your server is built
    # with the `ngx_pagespeed` module, uncomment this line to disable it.
    #pagespeed off;

    # The settings allows you to optimize the HTTP2 bandwitdth.
    # See https://blog.cloudflare.com/delivering-http-2-upload-speed-improvements/
    # for tunning hints
    client_body_buffer_size 512k;

    # HTTP response headers borrowed from Nextcloud `.htaccess`
    add_header Referrer-Policy                      "no-referrer"   always;
    add_header X-Content-Type-Options               "nosniff"       always;
    add_header X-Download-Options                   "noopen"        always;
    add_header X-Frame-Options                      "SAMEORIGIN"    always;
    add_header X-Permitted-Cross-Domain-Policies    "none"          always;
    add_header X-Robots-Tag                         "none"          always;
    add_header X-XSS-Protection                     "1; mode=block" always;

    # Remove X-Powered-By, which is an information leak
    fastcgi_hide_header X-Powered-By;

    # Specify how to handle directories -- specifying `/index.php$request_uri`
    # here as the fallback means that Nginx always exhibits the desired behaviour
    # when a client requests a path that corresponds to a directory that exists
    # on the server. In particular, if that directory contains an index.php file,
    # that file is correctly served; if it doesn't, then the request is passed to
    # the front-end controller. This consistent behaviour means that we don't need
    # to specify custom rules for certain paths (e.g. images and other assets,
    # `/updater`, `/ocm-provider`, `/ocs-provider`), and thus
    # `try_files $uri $uri/ /index.php$request_uri`
    # always provides the desired behaviour.
    index index.php index.html /index.php$request_uri;

    # Rule borrowed from `.htaccess` to handle Microsoft DAV clients
    location = / {
        if ( $http_user_agent ~ ^DavClnt ) {
            return 302 /remote.php/webdav/$is_args$args;
        }
    }

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    # Make a regex exception for `/.well-known` so that clients can still
    # access it despite the existence of the regex rule
    # `location ~ /(\.|autotest|...)` which would otherwise handle requests
    # for `/.well-known`.
    location ^~ /.well-known {
        # The rules in this block are an adaptation of the rules
        # in `.htaccess` that concern `/.well-known`.

        location = /.well-known/carddav { return 301 /remote.php/dav/; }
        location = /.well-known/caldav  { return 301 /remote.php/dav/; }

        location /.well-known/acme-challenge    { try_files $uri $uri/ =404; }
        location /.well-known/pki-validation    { try_files $uri $uri/ =404; }

        # Let Nextcloud's API for `/.well-known` URIs handle all other
        # requests by passing them to the front-end controller.
        return 301 /index.php$request_uri;
    }

    # Rules borrowed from `.htaccess` to hide certain paths from clients
    location ~ ^/(?:build|tests|config|lib|3rdparty|templates|data)(?:$|/)  { return 404; }
    location ~ ^/(?:\.|autotest|occ|issue|indie|db_|console)                { return 404; }

    # Ensure this block, which passes PHP files to the PHP process, is above the blocks
    # which handle static assets (as seen below). If this block is not declared first,
    # then Nginx will encounter an infinite rewriting loop when it prepends `/index.php`
    # to the URI, resulting in a HTTP 500 error response.
    location ~ \.php(?:$|/) {
        # Required for legacy support
        rewrite ^/(?!index|remote|public|cron|core\/ajax\/update|status|ocs\/v[12]|updater\/.+|oc[ms]-provider\/.+|.+\/richdocumentscode\/proxy) /index.php$request_uri;

        fastcgi_split_path_info ^(.+?\.php)(/.*)$;
        set $path_info $fastcgi_path_info;

        try_files $fastcgi_script_name =404;

        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_param HTTPS on;
        fastcgi_read_timeout 600;
fastcgi_send_timeout 600;
fastcgi_connect_timeout 600;
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
send_timeout 600;
        fastcgi_param modHeadersAvailable true;         # Avoid sending the security headers twice
        fastcgi_param front_controller_active true;     # Enable pretty urls
        fastcgi_pass php-handler;

        fastcgi_intercept_errors on;
        fastcgi_request_buffering off;

        fastcgi_max_temp_file_size 0;
    }

    location ~ \.(?:css|js|svg|gif|png|jpg|ico|wasm|tflite|map)$ {
        try_files $uri /index.php$request_uri;
        add_header Cache-Control "public, max-age=15778463, $asset_immutable";
        access_log off;     # Optional: Don't log access to assets

        location ~ \.wasm$ {
            default_type application/wasm;
        }
    }

    location ~ \.woff2?$ {
        try_files $uri /index.php$request_uri;
        expires 7d;         # Cache-Control policy borrowed from `.htaccess`
        access_log off;     # Optional: Don't log access to assets
    }

    # Rule borrowed from `.htaccess`
    location /remote {
        return 301 /remote.php$request_uri;
    }

    location / {
        try_files $uri $uri/ /index.php$request_uri;
    }
}
```  
### 配置文件  
```
<?php
$CONFIG = array (
  'instanceid' => 'oclr3dphcljr',
  'passwordsalt' => 'sUw+4f8vNgz4gis7U2dwLa+7mwLlDJ',
  'secret' => 'R+vOLI7rFQ5e+H0bhDcSoGhvzdyyyKqW6P/Ax8D64Fh1MQwm',
  'trusted_domains' => 
  array (
    0 => 'www.exploit-db.xyz:15006',
  ),
  'datadirectory' => '/etc/nginx/html/nextcloud/data',
  'dbtype' => 'mysql',
  'version' => '25.0.3.2',
  'overwrite.cli.url' => 'https://www.exploit-db.xyz:15006',
  'dbname' => 'nextcloud',
  'dbhost' => 'localhost:3306',
  'dbport' => '',
  'default_phone_region' => 'CN',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'oc_exploit',
  'dbpassword' => 'KL}!>5tDhp)2~#)8)D5kJ7WeG3-z=>',
  'installed' => true,
  'memcache.local' => '\\OC\\Memcache\\Redis',
  'filelocking.enabled' => true,
  'memcache.locking' => '\\OC\\Memcache\\Redis',
  'memcache.distributed' => '\\OC\\Memcache\\Redis',
  'redis' => 
  array (
    'host' => 'localhost',
    'port' => 6379,
  ),
  'enabledPreviewProviders' => 
  array (
    0 => 'OC\\Preview\\PNG',
    1 => 'OC\\Preview\\JPEG',
    2 => 'OC\\Preview\\GIF',
    3 => 'OC\\Preview\\HEIC',
    4 => 'OC\\Preview\\BMP',
    5 => 'OC\\Preview\\XBitmap',
    6 => 'OC\\Preview\\MP3',
    7 => 'OC\\Preview\\TXT',
    8 => 'OC\\Preview\\MarkDown',
    9 => 'OC\\Preview\\Movie',
  ),
  'global_aria2_config' => 
  array (
    'check-integrity' => 'true',
    'optimize-concurrent-downloads' => 'true',
    'continue' => 'true',
    'max-concurrent-downloads' => '999',
    'bt-tracker' => 'http://1337.abcvg.info:80/announce,http://207.241.226.111:6969/announce,http://207.241.231.226:6969/announce,http://504e163a.host.njalla.net:6969/announce,http://[2001:1b10:1000:8101:0:242:ac11:2]:6969/announce,http://[2a04:ac00:1:3dd8::1:2710]:2710/announce,http://bt.endpot.com:80/announce,http://bt.okmp3.ru:2710/announce,http://bt1.letpo.com:80/announce,http://chouchou.top:8080/announce,http://dht.dhtclub.com:666/announce,http://fe.dealclub.de:6969/announce,http://fosstorrents.com:6969/announce,http://incine.ru:6969/announce,http://nyaa.tracker.wf:7777/announce,http://open.acgnxtracker.com:80/announce,http://open.acgtracker.com:1096/announce,http://p2p.0g.cx:6969/announce,http://retracker.hotplug.ru:2710/announce,http://share.camoe.cn:8080/announce,http://t.acg.rip:6699/announce,http://torrentsmd.com:8080/announce,http://tr.cili001.com:8070/announce,http://tracker.birkenwald.de:6969/announce,http://tracker.bt4g.com:2095/announce,http://tracker.dler.com:6969/announce,http://tracker.dler.org:6969/announce,http://tracker.edkj.club:6969/announce,http://tracker.files.fm:6969/announce,http://tracker.gbitt.info:80/announce,http://tracker.ipv6tracker.ru:80/announce,http://tracker.lelux.fi:80/announce,http://tracker.mywaifu.best:6969/announce,http://tracker.opentrackr.org:1337/announce,http://tracker.qu.ax:6969/announce,http://tracker.sakurato.art:23333/announce,http://tracker.srv00.com:6969/announce,http://trackme.theom.nz:80/announce,http://v6-tracker.0g.cx:6969/announce,http://vps02.net.orel.ru:80/announce,http://wepzone.net:6969/announce,http://www.all4nothin.net:80/announce,.phphttp://www.wareztorrent.com:80/announce,https://1337.abcvg.info:443/announce,https://opentracker.i2p.rocks:443/announce,https://t1.hloli.org:443/announce,https://torrent-tracker.hama3.net:443/announce,https://tr.abiir.top:443/announce,https://tr.burnabyhighstar.com:443/announce,https://tracker.expli.top:443/announce,https://tracker.foreverpirates.co:443/announce,https://tracker.gbitt.info:443/announce,https://tracker.imgoingto.icu:443/announce,https://tracker.kuroy.me:443/announce,https://tracker.lelux.fi:443/announce,https://tracker.lilithraws.cf:443/announce,https://tracker.lilithraws.org:443/announce,https://tracker.loligirl.cn:443/announce,https://tracker.mlsub.net:443/announce,https://tracker.moeblog.cn:443/announce,https://tracker.tamersunion.org:443/announce,https://tracker1.520.jp:443/announce,https://trackers.mlsub.net:443/announce,https://trackme.theom.nz:443/announce,udp://184.105.151.166:6969/announce,udp://207.241.226.111:6969/announce,udp://207.241.231.226:6969/announce,udp://52.58.128.163:6969/announce,udp://6ahddutb1ucc3cp.ru:6969/announce,udp://9.rarbg.com:2810/announce,udp://91.216.110.52:451/announce,udp://[2001:1b10:1000:8101:0:242:ac11:2]:6969/announce,udp://[2001:470:1:189:0:1:2:3]:6969/announce,udp://[2a03:7220:8083:cd00::1]:451/announce,udp://[2a04:ac00:1:3dd8::1:2710]:2710/announce,udp://[2a0f:e586:f:f::81]:6969/announce,udp://aarsen.me:6969/announce,udp://acxx.de:6969/announce,udp://admin.52ywp.com:6969/announce,udp://aegir.sexy:6969/announce,udp://astrr.ru:6969/announce,udp://bedro.cloud:6969/announce,udp://black-bird.ynh.fr:6969/announce,udp://boysbitte.be:6969/announce,udp://bt.ktrackers.com:6666/announce,udp://bt1.archive.org:6969/announce,udp://bt2.archive.org:6969/announce,udp://camera.lei001.com:6969/announce,udp://chouchou.top:8080/announce,udp://concen.org:6969/announce,udp://creative.7o7.cx:6969/announce,udp://cutscloud.duckdns.org:6969/announce,udp://dht.bt251.com:6969/announce,udp://dns.xxtor.com:53/announce,udp://epider.me:6969/announce,udp://exodus.desync.com:6969/announce,udp://fe.dealclub.de:6969/announce,udp://fh2.cmp-gaming.com:6969/announce,udp://free.publictracker.xyz:6969/announce,udp://freedom.1776.ga:6969/announce,udp://htz3.noho.st:6969/announce,udp://ipv4.tracker.harry.lu:80/announce,udp://ipv6.tracker.monitorit4.me:6969/announce,udp://laze.cc:6969/announce,udp://mail.artixlinux.org:6969/announce,udp://mirror.aptus.co.tz:6969/announce,udp://moonburrow.club:6969/announce,udp://movies.zsw.ca:6969/announce,udp://new-line.net:6969/announce,udp://open.4ever.tk:6969/announce,udp://open.demonii.com:1337/announce,udp://open.dstud.io:6969/announce,udp://open.publictracker.xyz:6969/announce,udp://open.stealth.si:80/announce,udp://open.tracker.ink:6969/announce,udp://opentor.org:2710/announce,udp://opentracker.i2p.rocks:6969/announce,udp://opentracker.io:6969/announce,udp://p4p.arenabg.com:1337/announce,udp://private.anonseed.com:6969/announce,udp://psyco.fr:6969/announce,udp://public.publictracker.xyz:6969/announce,udp://rep-art.ynh.fr:6969/announce,udp://retracker.hotplug.ru:2710/announce,udp://retracker.lanta-net.ru:2710/announce,udp://run.publictracker.xyz:6969/announce,udp://sanincode.com:6969/announce,udp://slicie.icon256.com:8000/announce,udp://stargrave.org:6969/announce,udp://static.54.161.216.95.clients.your-server.de:6969/announce,udp://t.133335.xyz:6969/announce,udp://tamas3.ynh.fr:6969/announce,udp://thagoat.rocks:6969/announce,udp://thouvenin.cloud:6969/announce,udp://torrents.artixlinux.org:6969/announce,udp://tr.bangumi.moe:6969/announce,udp://tr.cili001.com:8070/announce,udp://tracker-udp.gbitt.info:80/announce,udp://tracker.4.babico.name.tr:3131/announce,udp://tracker.altrosky.nl:6969/announce,udp://tracker.artixlinux.org:6969/announce,udp://tracker.auctor.tv:6969/announce,udp://tracker.beeimg.com:6969/announce,udp://tracker.birkenwald.de:6969/announce,udp://tracker.bitsearch.to:1337/announce,udp://tracker.bittor.pw:1337/announce,udp://tracker.ccp.ovh:6969/announce,udp://tracker.cubonegro.xyz:6969/announce,udp://tracker.cyberia.is:6969/announce,udp://tracker.ddunlimited.net:6969/announce,udp://tracker.dler.com:6969/announce,udp://tracker.dler.org:6969/announce,udp://tracker.filemail.com:6969/announce,udp://tracker.jonaslsa.com:6969/announce,udp://tracker.joybomb.tw:6969/announce,udp://tracker.leech.ie:1337/announce,udp://tracker.lelux.fi:6969/announce,udp://tracker.monitorit4.me:6969/announce,udp://tracker.openbittorrent.com:6969/announce,udp://tracker.openbtba.com:6969/announce,udp://tracker.opentrackr.org:1337/announce,udp://tracker.pimpmyworld.to:6969/announce,udp://tracker.publictracker.xyz:6969/announce,udp://tracker.qu.ax:6969/announce,udp://tracker.skynetcloud.site:6969/announce,udp://tracker.skyts.net:6969/announce,udp://tracker.srv00.com:6969/announce,udp://tracker.swateam.org.uk:2710/announce,udp://tracker.theoks.net:6969/announce,udp://tracker.tiny-vps.com:6969/announce,udp://tracker.torrent.eu.org:451/announce,udp://tracker.yangxiaoguozi.cn:6969/announce,udp://tracker.zaluan.xyz:6969/announce,udp://tracker1.bt.moack.co.kr:80/announce,udp://tracker1.myporn.club:9337/announce,udp://tracker6.lelux.fi:6969/announce,udp://trackerb.jonaslsa.com:6969/announce,udp://uploads.gamecoast.net:6969/announce,udp://v1046920.hosted-by-vdsina.ru:6969/announce,udp://v2.iperson.xyz:6969/announce,udp://wepzone.net:6969/announce,udp://www.peckservers.com:9000/announce,udp://www.torrent.eu.org:451/announce,udp://zecircle.xyz:6969/announce,ws://hub.bugout.link:80/announce,wss://tracker.openwebtorrent.com:443/announce',
  ),
  'app_install_overwrite' => 
  array (
    0 => 'duplicatefinder',
  ),
);
```
## GitLab局域网搭建  
```
upstream gitlab {
  # 7.x 版本在此位置
  # server unix:/var/opt/gitlab/gitlab-rails/tmp/sockets/gitlab.socket;
  # 8.0 位置
 #server unix:/var/opt/gitlab/gitlab-rails/sockets/gitlab.socket;
 server unix:/var/opt/gitlab/gitlab-workhorse/socket fail_timeout=0; 
}

server {
  listen *:15007 ssl http2;
  listen [::]:15007 ssl http2;
  server_name www.exploit-db.xyz;   # 请修改为你的域名
  ssl_protocols  TLSv1.1 TLSv1.2 TLSv1.3;
  server_tokens off;     # don't show the version number, a security best practice
  root /opt/gitlab/embedded/service/gitlab-rails/public;

  # Increase this if you want to upload large attachments
  # Or if you want to accept large git objects over http
  client_max_body_size 250m;

  # individual nginx logs for this gitlab vhost
  access_log  /var/log/gitlab/nginx/gitlab_access.log;
  error_log   /var/log/gitlab/nginx/gitlab_error.log;
  ssl_stapling on;
resolver 8.8.8.8 8.8.4.4 223.5.5.5 valid=300s;
resolver_timeout 5s;
  ssl_certificate /home/exploit/SSL/zhengshu.csr;
  ssl_certificate_key /home/exploit/SSL/exploit-db.xyz.key;
  ssl_client_certificate  /home/exploit/SSL/CA.crt; 
  location / {
    # serve static files from defined root folder;.
    # @gitlab is a named location for the upstream fallback, see below
    try_files $uri $uri/index.html $uri.html @gitlab;
  }

  # if a file, which is not found in the root folder is requested,
  # then the proxy pass the request to the upsteam (gitlab unicorn)
  location @gitlab {
    # If you use https make sure you disable gzip compression 
    # to be safe against BREACH attack

    proxy_read_timeout 300; # Some requests take more than 30 seconds.
    proxy_connect_timeout 300; # Some requests take more than 30 seconds.
    proxy_redirect     off;

    proxy_set_header   X-Forwarded-Proto $scheme;
    proxy_set_header   Host              $http_host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Frame-Options   SAMEORIGIN;

    proxy_pass http://gitlab;
  }

  # Enable gzip compression as per rails guide: http://guides.rubyonrails.org/asset_pipeline.html#gzip-compression
  # WARNING: If you are using relative urls do remove the block below
  # See config/application.rb under "Relative url support" for the list of
  # other files that need to be changed for relative url support
  location ~ ^/(assets)/  {
    root /opt/gitlab/embedded/service/gitlab-rails/public;
    # gzip_static on; # to serve pre-gzipped version
    expires max;
    add_header Cache-Control public;
  }

  error_page 502 /502.html;
}
```
