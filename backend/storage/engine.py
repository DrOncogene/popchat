"""
the storage engine
"""
from os import getenv
from typing import Type
from mongoengine import connect

from models.user import User
from models.chat import Chat
from models.room import Room


T = User | Chat | Room

DB_NAME = getenv('DB_NAME')
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')
DB_USER = getenv('DB_USER')
DB_PASSWD = getenv('DB_PASSWD')


class Engine:
    """db engine"""

    def load(self):
        connect('popchat')

    def get_by_id(self, model: Type[T], id: str) -> T:
        """fetches a document by id"""
        return model.objects(id=id).first()
    
    def get_by_username(self, name: str) -> User:
        """fetches a user by username"""
        return User.objects(username=name).first()
    
    def get_by_email(self, email: str) -> User:
        """fetches a user by email"""
        return User.objects(email=email).first()
    
    def get_by_auth_token(self, token: str) -> User:
        """fetches a user by auth token"""
        return User.objects(auth_token=token).first()
    
    def get_by_reset_token(self, token: str) -> User:
        """fetches a user by reset token"""
        return User.objects(reset_token=token).first()
