"""
defines configuration classes
"""
from os import path, environ

from dotenv import load_dotenv


# get the current dir
curr_dir = path.abspath(path.dirname(__file__))
# get the .env file path (curr_dir/../.env)
env_dir = path.join(curr_dir, '..', '.env')

class Config:
    """common config vars"""
    load_dotenv(env_dir)
    SECRET_KEY = environ.get('SECRET_KEY')
    JSONIFY_PRETTYPRINT_REGULAR = True


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
