#!/usr/bin/env bash

nginx_conf_filename="popchat-api.conf"
nginx_conf="/etc/nginx/sites-available/$nginx_conf_filename"

sudo apt-get update
sudo apt-get install -y --no-upgrade nginx

sudo printf %s " upstream popchat-api {
        hash $request_uri consistent;

        server chat-api:8000;
        server chat-api:8001;
}

server {
    listen 80;
    listen [::]:80;
    root /var/www/html;
    index index.html;
    server_name pop-chat-api.droncogene.com;

    location ~ /api {
        # Redirect to api
        proxy_pass http://localhost:8000;
    }

    location ~ /socket.io {
        proxy_pass http://localhost:8000;
        
        # Websocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_no_cache \$http_upgrade;
    }
}
" | sudo tee "$nginx_conf" > /dev/null

sudo rm -f "/etc/nginx/sites-enabled/$nginx_conf_filename"
sudo ln -s "$nginx_conf" /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

