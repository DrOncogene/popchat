# """
# defines configuration classes
# """
from os import environ, path, getenv
from datetime import timedelta

from pydantic import BaseSettings
# from dotenv import load_dotenv
# # from redis import Redis

# get the current dir
# curr_dir = path.abspath(path.dirname(__file__))
# get the .env file path (curr_dir/.env)
# env_dir = path.join(curr_dir, '.env')
# load_dotenv(env_dir)
# print(environ.get('FLASK_SECRET_KEY'))


class Settings(BaseSettings):
    """common config vars"""
    authjwt_secret_key: str
    authjwt_token_location: set[str] = {'cookies'}
    authjwt_access_token_expires: timedelta = timedelta(days=1)
    authjwt_access_cookie_key = '_popchat_auth'
    authjwt_cookie_max_age = 24 * 60 * 60
    authjwt_cookie_samesite = 'strict'

    class Config:
        """config class"""
        env_file = '.env'
        env_file_encoding = 'utf-8'


# class ProdConfig(Config):
#     """production configs"""
#     FLASK_ENV = 'production'
#     TESTING = False
#     DEBUG = False


# class DevConfig(Config):
#     """dev configs"""
#     FLASK_ENV = 'development'
#     TESTING = True
#     DEBUG = True
