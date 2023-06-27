#!/usr/bin/env python3

"""
the wsgi server entry point
"""
from api.chat import *
from api import create_app

app = create_app()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('wsgi:app', reload=True)
