#!/usr/bin/env python3
"""
init file - defines the factory function
"""
from functools import lru_cache
from contextlib import asynccontextmanager

from socketio import AsyncServer, ASGIApp, AsyncAioPikaManager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.routers.auth import auth_router
from app.db import init_db, get_mongo_uri, get_rabbitmq_uri


sio = AsyncServer(
    async_mode='asgi',
    client_manager=AsyncAioPikaManager(get_rabbitmq_uri()),
    cors_allowed_origins=[]
)

sio_app = ASGIApp(
    socketio_server=sio,
)

ORIGINS = [
    'http://127.0.0.1:5173',
    'http://127.0.0.1:80',
    'https://popchat.droncogene.com',
]


@asynccontextmanager
async def lifecycle(app: FastAPI):
    """app lifecycle"""
    # logger.info('starting app')
    await init_db(get_mongo_uri())
    yield
    # logger.info('stopping app')


def create_app() -> FastAPI:
    """app factory function"""
    app = FastAPI(lifespan=lifecycle)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(auth_router)
    app.mount('/', app=sio_app)

    @app.get('/api')
    async def root():
        return {'message': 'Welcome to the PopChat API!'}

    return app
