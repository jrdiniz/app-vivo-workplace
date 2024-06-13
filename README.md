## Environment

The project use python-dotenv library, so you need the .env file on root directory of the project:

 - Develop Environment 

```
FLASK_APP=app
FLASK_DEBUG=True
FLASK_CONFIG_FILE=config.DevelopmentConfig
SECRET_KEY=

MYSQL_ADDRESS=
MYSQL_DATABASE=
MYSQL_USERNAME=
MYSQL_PASSWORD=
```

 - Production Environment

```
FLASK_APP=app
FLASK_DEBUG=False
FLASK_CONFIG_FILE=config.ProductionConfig
SECRET_KEY=

MYSQL_ADDRESS=
MYSQL_DATABASE=
MYSQL_USERNAME=
MYSQL_PASSWORD=
```

## Deploy - Ansible

``` 
sudo ansible-playbook deploy.yml
```

## Deploy - Manual

### Install Application

```
~$ sudo adduser --home /u/htdocs/webpoint/vivoempresas/public_html --gid 480 --shell /bin/bash vivoempresas
~$ cd /u/htdocs/webpoint/vivoempresas/public_html
~$ sudo git clone https://github.com/jrdiniz/app-vivoempresas-webinar.git .
~$ sudo python -m venv ./env
~$ ./bin/source/active
~$ pip install -r requeriments.txt
```

### Web Server - NGINX

#### vHost - /etc/nginx/conf.d/vivoempresas.conf

```
server {
    listen 80;
    server_name vivoempresas.terra.com.br;
    return 301 https://vivoempresas.terra.com.br$request_uri;
}

server {
    listen 443 ssl;
    server_name vivoempresas.terra.com.br;

    # Clickjacking
    add_header X-Frame-Options "SAMEORIGIN";

    access_log  /var/log/nginx/vivoempresas-access.log;
    error_log  /var/log/nginx/vivoempresas-error.log;

    root /u/htdocs/webpoint/vivoempresas/public_html;

    location / {*
        proxy_pass         http://127.0.0.1:8500/;
        proxy_redirect     off;

        proxy_set_header   Host                 $host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
        proxy_read_timeout 120;
        proxy_connect_timeout 30s;
        client_max_body_size 5M;
    }

    location /socket.io {
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:8500/socket.io;

    }
    
    location ~* \.(asf|asx|wax|wmv|wmx|avi|bmp|class|divx|doc|docx|eot|exe|gif|gz|gzip|ico|jpg|jpeg|jpe|mdb|mid|midi|mov|qt|mp3|m4a|mp4|m4v|mpeg|mpg|mpe|mpp|odb|odc|odf|odg|odp|ods|odt|ogg|ogv|otf|pdf|png|pot|pps|ppt|pptx|ra|ram|svg|svgz|swf|tar|t?gz|tif|tiff|ttf|wav|webm|wma|woff|wri|xla|xls|xlsx|xlt|xlw|zip)$ {
        expires 31536000s;
        access_log off;
        log_not_found off;
        add_header Pragma public;
        add_header Cache-Control "max-age=31536000, public";
    }
    
    location ~ /\. {
        access_log off;
        log_not_found off;
        deny all;
    }
    
    location ^~ /static/  {
        include  /etc/nginx/mime.types;
        root /u/htdocs/webpoint/vivoempresas/public_html/webinar;
    }
}
```

### Database Configuration

#### Create database

```
mysql -u <mysql_user> -h <mysql_address> -p<mysql_user_password> -Bse "CREATE DATABASE vivoempresas_webinar_db CHARACTER SET Latin1 COLLATE = latin1_general_ci;"
```

#### Create database user

``` 
mysql -u <mysql_user> -h <mysql_address> -p<mysql_user_password> -Bse "GRANT ALL PRIVILEGES ON vivoempresas_webinar_db.* to vivoempresas_webinar@'%' identified by '<user_password>';"
```

### Create systemmd service

Copy the systemd script to /etc/systemd/system/

```
cp vivoempresas.service /etc/systemd/system/
```

Restart de daemon

```
sudo systemctl daemon-reload
```

Run the service

```
sudo systemctl start vivoempresas
```

Debug systemd

```
journalctl -u vivoempresas
```