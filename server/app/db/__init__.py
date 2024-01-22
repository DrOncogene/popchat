#!/usr/bin/env python3
"""
Instantiates a database storage engine instance.
"""
from redis.exceptions import ConnectionError
from .engine import Cache, init_db, get_mongo_uri, get_rabbitmq_uri

from app.settings import settings


SESSION_CACHE = Cache(
    ttl=settings.REDIS_TTL,
    db=settings.REDIS_SESSION_DB,
)
SOCKETIO_CACHE = Cache(
    ttl=settings.REDIS_TTL,
    db=settings.REDIS_SOCKETIO_DB,
)
if not SESSION_CACHE.ping() or not SOCKETIO_CACHE.ping():
    raise ConnectionError("redis cache is not available")
