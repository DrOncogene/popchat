"""
the wsgi server entry point
"""
from os import environ

from app import create_app


if __name__ == '__main__':
    app, socketio = create_app()

    HOST = environ.get('HOST') or 'localhost'
    PORT = environ.get('PORT') or 5000
    DEBUG = app.config.get('DEBUG')

    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
