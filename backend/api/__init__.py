#!/usr/bin/env python3
"""
init file - defines the factory function
"""
from fastapi import FastAPI
from fastapi_socketio import SocketManager
from .auth import auth_router

app = FastAPI()
sio = SocketManager(app=app, cors_allowed_origins='*')
app.include_router(auth_router)
