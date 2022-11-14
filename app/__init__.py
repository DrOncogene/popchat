"""
init file - defines the factory function
"""
from os import environ

from flask import Flask
from flask_socketio import SocketIO

from .config import DevConfig


def create_app():
    """the app factory"""
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins=r'*')

    # load config files
    app.config.from_object(DevConfig)

    return app, socketio
