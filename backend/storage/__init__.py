#!/usr/bin/env python3

"""
Instantiates a database storage engine instance.
"""
from storage.engine import Engine


db = Engine()
db.load()
