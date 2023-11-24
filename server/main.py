#!/usr/bin/env python3

"""
the wsgi server entry point
"""
from app.routers.chat import *
from app import create_app
from app.settings import settings


app = create_app()


if __name__ == '__main__':
    import uvicorn
    HOST = settings.APP_HOST
    PORT = settings.APP_PORT
    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)
