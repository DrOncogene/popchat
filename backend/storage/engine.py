#!/usr/bin/env python3

"""
Defines the storage engine.
"""

from os import getenv
from typing import Type
from mongoengine import connect
from mongoengine.queryset.visitor import Q
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

    def match_users(self, search_term: str = '') -> list[User]:
        """fetches a list of users that match the search term"""
        return User.objects(username__icontains=search_term)

    def get_by_id(self, model: Type[T], id: str) -> T | None:
        """Fetches a document by id"""

        return model.objects(id=id).first()


    def get_by_username(self, name: str) -> User | None:
        """fetches a user by username"""
        return User.objects(username=name).first()


    def get_by_email(self, email: str) -> User | None:
        """fetches a user by email"""
        return User.objects(email=email).first()


    def get_by_auth_token(self, token: str) -> User | None:
        """fetches a user by auth token"""
        return User.objects(auth_token=token).first()


    def get_by_reset_token(self, token: str) -> User | None:
        """fetches a user by reset token"""
        return User.objects(reset_token=token).first()

    def get_chats_by_user(self, user: User) -> list[Chat | Room]:

    def get_chats_by_user(self, user: User) -> list[Chat]:
        """
        fetches all active chats and rooms for a user

        """
        return Chat.objects(Q(user_1=user.username) |
                            Q(user_2=user.username)).exclude('messages')

    def get_rooms_by_user(self, user: User) -> list[Room]:
        """
        fetches all active chats and rooms for a user

        """
        return (Room.objects(members__in=[user.username])
                .exclude('messages', 'members'))
