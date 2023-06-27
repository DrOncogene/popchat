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
