"""
initialize a storage engine
instance
"""
from .engine import Engine


db = Engine()
db.load()
