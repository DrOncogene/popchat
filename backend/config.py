"""
defines configuration classes
"""
from datetime import timedelta

from pydantic import BaseSettings


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


class DBSettings(BaseSettings):
    """db config vars"""
    DB_NAME: str = 'popchat'
    DB_PORT: int = 27017
    DB_HOST: str = 'localhost'
    DB_USER: str = None
    DB_PASSWD: str = None

    class Config:
        """config class"""
        env_file = '.env'
        env_file_encoding = 'utf-8'
