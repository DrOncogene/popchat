"""
the wsgi server entry point
"""
from os import environ

from config import DevConfig, ProdConfig
from app import sio, create_app
from app.chat import chat

config = environ.get('FLASK_DEBUG')

if config == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)
print(app.config['SECRET_KEY'])

if __name__ == '__main__':
    HOST = environ.get('HOST') or 'localhost'
    PORT = environ.get('PORT') or 5000
    DEBUG = app.config.get('DEBUG')

    sio.run(app, host=HOST, port=PORT, debug=DEBUG)
