"""
the wsgi server entry point
"""
from api import app, sio


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('wsgi:app', reload=True)
