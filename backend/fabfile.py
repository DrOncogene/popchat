#!/usr/bin/env python3
"""
fabric file for preping the server
"""
from fabric import task


@task
def docker_setup(ctx):
    """
    installs docker and docker compose
    on the backend server
    CLI command to run:
    fab --hosts `host strings` docker-setup
    """

    res = ctx.run('sudo dpkg --list | grep docker', warn=True)
    if res.ok:
        print('Docker found, removing existing installation... 🔃')
        ctx.run('sudo systemctl stop docker.service')
        ctx.run('sudo apt-get purge -y docker.io docker-doc \
                docker-compose podman-docker containerd runc')
        ctx.run('sudo apt-get purge -y docker-ce docker-ce-cli \
                containerd.io docker-buildx-plugin docker-compose-plugin')

    print('Installing Docker 🐳...\n')
    ctx.run('sudo apt-get -y autoremove')
    ctx.run('sudo apt-get update')
    res = ctx.run('sudo apt-get install -y docker-ce docker-ce-cli \
                  containerd.io docker-buildx-plugin \
                  docker-compose-plugin', warn=True)
    if res.failed:
        print('❌ FAILED TO START DOCKER SERVICE, retrying in 20 seconds...')
        ctx.run('sleep 20')

    ctx.run('set -e sudo groupadd docker')
    ctx.run('sudo usermod -aG docker "$USER"')
    res = ctx.run('sudo systemctl status docker.service', warn=True)
    if res.failed:
        print('❌ FAILED TO START DOCKER SERVICE, retrying in 30 seconds...')
        ctx.run('sleep 30')

    ctx.run('sudo systemctl start docker.service', warn=True)
    res = ctx.run('sudo systemctl status docker.service', warn=True)
    if res.failed:
        print('❌ DOCKER INSTALLATION FAILED, \
              kindly check the logs and retry later')
        return

    print('\nDOCKER INSTALLED SUCCESSFULLY ✅')


@task
def nginx_setup(ctx):
    """
    installs nginx on the backend server
    """
    ctx.put('./setup-nginx.sh', '/tmp/popchat/setup_nginx.sh')
    ctx.run('chmod +x /tmp/popchat/setup_nginx.sh')
    ctx.run('sudo /tmp/popchat/setup_nginx.sh')


@task
def ssl_setup(ctx):
    """
    sets up ssl certificates on the server
    using certbot
    """
    ctx.run('sudo snap install core; sudo snap refresh core')
    ctx.run('sudo apt remove certbot')
    ctx.run('sudo snap install --classic certbot')
    ctx.run('sudo ln -s /snap/bin/certbot /usr/bin/certbot', warn=True)
    ctx.run('sudo certbot -n --agree-tos --nginx -m mypythtesting@gmail.com -d\
             popchat-api.droncogene.com')
    ctx.run('sudo systemctl status snap.certbot.renew.service')
    ctx.run('sudo certbot renew --dry-run')


@task
def ssl_reconfigure(ctx):
    """
    reconfigures nginx after ssl setup
    """
    ctx.run('sudo certbot --nginx reconfigure')
    ctx.run('sudo nginx -t')
    ctx.run('sudo systemctl restart nginx')


@task
def run_containers(ctx):
    """
    runs the docker containers
    """
    ctx.run('mkdir -p /tmp/popchat')
    ctx.put('./docker-compose.yml', '/tmp/popchat/docker-compose.yml')
    ctx.run('docker compose -f /tmp/popchat/docker-compose.yml up -d')
