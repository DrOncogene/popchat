#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y --no-upgrade nginx

LINE=$(grep -Eno "^\s*location / {" /etc/nginx/sites-available/default | cut -d : -f 1 | head -n 1)
EXIST=$(grep -Eco "^/s*location ~ /api/ {" /etc/nginx/sites-available/default)
EXIST2=$(grep -Eco "^/s*location ~ /socket.io/ {" /etc/nginx/sites-available/default)


if [ "$EXIST" -le 0 ]
then
    sudo sed -i "$LINE i\ \tlocation \~ /api/ {\n\t\t# Redirect to api\n\t\tproxy_pass http://localhost:8000;\n\t}\n\n" /etc/nginx/sites-available/default
fi

if [ "$EXIST2" -le 0 ]
then
    LINE2=$(grep -Eno "^\s*location / {" /etc/nginx/sites-available/default | cut -d : -f 1 | head -n 1)
    sudo sed -i "$LINE2 i\ \tlocation \~ /socket.io/ {\n\t\t\tproxy_pass http://localhost:8000;\n\n\t\t# Websocket Support\n\t\tproxy_http_version 1.1;\n\t\tproxy_set_header Upgrade \$http_upgrade;\n\t\tproxy_set_header Connection \"upgrade\";\n\t\tproxy_set_header Host \$host;\n\n\t\tproxy_cache_bypass \$http_upgrade;\n\t\tproxy_no_cache \$http_upgrade;\n\t}\n\n" /etc/nginx/sites-available/default
fi

sudo nginx -t
sudo systemctl restart nginx
