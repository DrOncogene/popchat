"""
defines configuration classes
"""
from os import environ, path, getenv
from datetime import timedelta

from dotenv import load_dotenv
# from redis import Redis

# get the current dir
curr_dir = path.abspath(path.dirname(__file__))
# get the .env file path (curr_dir/.env)
env_dir = path.join(curr_dir, '.env')
load_dotenv(env_dir)
print(environ.get('FLASK_SECRET_KEY'))
# get redis server params
redis_host = getenv( 'REDIS_HOST') or 'localhost'
redis_port = getenv('REDIS_PORT') or 6379

class Config:
    """common config vars"""
    SECRET_KEY = environ.get('FLASK_SECRET_KEY')
    JSONIFY_PRETTYPRINT_REGULAR = True
    REMEMBER_COOKIE_DURATION = timedelta(hours=6.0)
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_NAME = 'popchat'
    # SESSION_PROTECTION = 'strong'
    # SESSION_TYPE = 'redis'
    # SESSION_USE_SIGNER = True
    # SESSION_REDIS = Redis(host=redis_host, port=redis_port)
    # PERMANENT_SESSION_LIFETIME = timedelta(hours=6.0)


class ProdConfig(Config):
    """production configs"""
    FLASK_ENV = 'production'
    TESTING = False
    DEBUG = False


class DevConfig(Config):
    """dev configs"""
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
