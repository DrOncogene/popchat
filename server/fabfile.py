#!/usr/bin/env python3
"""
fabric file for preping the server
"""
from os import getenv

from fabric import task
from fabric.connection import Context
from invoke.watchers import Responder


ENV_FILE = getenv('ENV_FILE', '.popchat.env')


@task
def docker_setup(ctx: Context):
    """
    installs docker and docker compose
    on the backend server
    CLI command to run:
    fab --hosts `host strings` docker-setup
    """

    res = ctx.run('sudo dpkg -l | grep -i docker', warn=True)
    if res.ok:
        print('Removing any existing installation... 🔃')
        ctx.run('sudo systemctl stop docker.service', warn=True)
        ctx.run('for pkg in docker.io docker-doc docker-compose \
                  docker-compose-v2 podman-docker containerd runc; \
                  do sudo apt-get remove $pkg; done', warn=True)
        ctx.run('sudo apt-get -y autoremove')

    print('Installing Docker 🐳...\n')
    ctx.run('sudo apt-get update')
    ctx.run('sudo apt-get install -y ca-certificates curl gnupg')
    ctx.run('sudo install -m 0755 -d /etc/apt/keyrings')
    ctx.run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
            | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg', warn=True)
    ctx.run('sudo chmod a+r /etc/apt/keyrings/docker.gpg')
    ctx.run(
        'echo "deb [arch="$(dpkg --print-architecture)" \
        signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
    )
    ctx.run('sudo apt-get update')
    res = ctx.run('sudo apt-get install -y docker-ce docker-ce-cli \
                  containerd.io docker-buildx-plugin \
                  docker-compose-plugin', warn=True)
    if res.failed:
        print('❌ FAILED TO INSTALL DOCKER')
        return

    ctx.run('set -e sudo groupadd docker')
    ctx.run('sudo usermod -aG docker "$USER"')
    ctx.run('sudo systemctl status docker.service', warn=True)
    res = ctx.run('sudo systemctl start docker.service', warn=True)
    if res.failed:
        print('❌ DOCKER INSTALLATION FAILED, \
              kindly check the logs and retry later')
        return

    ctx.run('sudo systemctl status docker.service', warn=True)
    print('\nDOCKER INSTALLED SUCCESSFULLY ✅')


@task
def nginx_setup(ctx: Context):
    """
    installs nginx on the backend server
    """
    ctx.run('mkdir -p /tmp/popchat')
    ctx.put('./setup-nginx.sh', '/tmp/popchat/setup_nginx.sh')
    ctx.run('chmod +x /tmp/popchat/setup_nginx.sh')
    ctx.run('sudo /tmp/popchat/setup_nginx.sh')


@task
def ssl_setup(ctx: Context):
    """
    sets up ssl certificates on the server
    using certbot
    """
    print('\nInstalling and setting up Certbot 📜...')
    ctx.run('sudo snap install core; sudo snap refresh core')
    ctx.run('sudo systemctl stop snap.certbot.renew.timer', warn=True)
    ctx.run('sudo systemctl stop snap.certbot.renew.service', warn=True)
    ctx.run('sudo snap remove certbot')
    ctx.run('sudo snap install --classic certbot')
    ctx.run('sudo ln -sf /snap/bin/certbot /usr/bin/certbot', warn=True)
    ctx.run('sudo certbot -n --agree-tos --nginx -m mypythtesting@gmail.com -d\
             pop-chat-api.droncogene.com', warn=True)
    ctx.run('sudo systemctl status snap.certbot.renew.service', warn=True)
    ctx.run('sudo certbot renew --dry-run')


@task
def ssl_reconfigure(ctx: Context):
    """
    reconfigures nginx after ssl setup
    """
    responder = Responder(
        pattern=r'Press 1 \[enter\] to confirm',
        response='1\n',
    )
    print('\nReconfiguring Nginx to use certbot... 📜')
    ctx.run('sudo certbot --nginx reconfigure', watchers=[responder])
    ctx.run('sudo nginx -t')
    ctx.run('sudo systemctl restart nginx')


@task
def set_envs(ctx: Context):
    """
    sets the environment variables
    """
    ctx.run('mkdir -p /tmp/popchat')
    ctx.put('./.env', f'/tmp/popchat/{ENV_FILE}')


@task
def run_containers(ctx: Context):
    """
    runs the docker containers
    """
    print('Spinning up the containers... 🚀')
    ctx.put('./docker-compose.yml', '/tmp/popchat/docker-compose.yml')
    ctx.run(f"ENV_FILE=/tmp/popchat/{ENV_FILE}\
            docker compose -f /tmp/popchat/docker-compose.yml up -d")
    ctx.run(f'rm /tmp/popchat/{ENV_FILE}')


@task
def deploy(ctx: Context):
    """
    deploys the app to the server
    """
    # docker_setup(ctx)
    nginx_setup(ctx)
    ssl_setup(ctx)
    ssl_reconfigure(ctx)
    set_envs(ctx)
    run_containers(ctx)
