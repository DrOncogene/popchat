"""
initialize a storage engine
instance
"""
from redis.exceptions import ConnectionError
from .engine import Engine, Cache


db = Engine()
db.load()

cache = Cache()
if not cache.ping():
    raise ConnectionError('redis cache is not available')
