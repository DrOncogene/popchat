#!/usr/bin/env python3

"""
Defines the storage engine.
"""

from os import getenv
from typing import Type
from mongoengine import connect
from models.user import User
from models.chat import Chat
from models.room import Room


T = User | Chat | Room

# Must be provided from the environment.
# FIXME: Maybe have defaults as well??
DB_NAME = getenv('DB_NAME')
DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')
DB_USER = getenv('DB_USER')
DB_PASSWD = getenv('DB_PASSWD')


class Engine:
    """Represents a database storage engine."""

    # FIXME : Should preferrably use `DB_NAME` obtained from environment
    def load(self):
        connect('popchat')

    def get_by_id(self, model: Type[T], id: str) -> T:
        """Fetches a document by id"""

        return model.objects(id=id).first()

    def get_by_username(self, username: str) -> User:
        """Fetches a `User` by username"""

        return User.objects(username=username).first()

    def get_by_email(self, email: str) -> User:
        """Fetches a `User` by email"""

        return User.objects(email=email).first()

    def get_by_auth_token(self, auth_token: str) -> User:
        """Fetches a `User` by authentication token"""

        return User.objects(auth_token=auth_token).first()

    def get_by_reset_token(self, reset_token: str) -> User:
        """Fetches a user by reset token"""

        return User.objects(reset_token=reset_token).first()
