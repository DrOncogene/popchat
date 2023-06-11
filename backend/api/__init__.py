#!/usr/bin/env python3
"""
init file - defines the factory function
"""
from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .sockets import sio_app
from .auth import auth_router
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from config import Settings


ORIGINS = [
    'http://localhost:5173'
]


@AuthJWT.load_config
@lru_cache
def get_config():
    return Settings()


def create_app(config=None) -> FastAPI:
    """app factory function"""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(auth_router)
    app.mount('/', app=sio_app)

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    return app
