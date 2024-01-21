#!/usr/bin/env bash

nginx_conf_filename="default.conf"
nginx_conf="/etc/nginx/conf.d/$nginx_conf_filename"

printf %s " upstream popchat-api {
        hash \$request_uri-\$http_user_agent-\$remote_addr consistent;

        server server-chat-api-1:8000;
        server server-chat-api-2:8000;
}

server {
    listen 80;
    listen [::]:80;
    root /var/www/html;
    index index.html;
    server_name pop-chat-api.droncogene.com;

    location ~ /api {
        # Redirect to api
        proxy_pass http://popchat-api;
    }

    location ~ /chat {
        proxy_pass http://popchat-api;
        
        # Websocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_no_cache \$http_upgrade;
    }
}
" | tee "$nginx_conf" > /dev/null

nginx -t
nginx -g 'daemon off;'
