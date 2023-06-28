#!/usr/bin/env python3

"""
Defines the storage engine.
"""
from typing import Type
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from redis import Redis

from config import DBSettings, RedisSettings
from models.user import User
from models.chat import Chat
from models.room import Room


T = User | Chat | Room


class Engine:
    """db engine"""
    settings = DBSettings()
    DB_NAME = settings.DB_NAME
    DB_HOST = settings.DB_HOST
    DB_PORT = settings.DB_PORT
    DB_USER = settings.DB_USER
    DB_PASSWD = settings.DB_PASSWD

    def load(self):
        """connects to the db"""
        if self.DB_USER and self.DB_PASSWD:
            uri = (f'mongodb://{self.DB_USER}:{self.DB_PASSWD}'
                   f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')
        else:
            uri = f'mongodb://{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

        connect(host=uri)

    def match_users(self, search_term: str = '') -> list[User]:
        """fetches a list of users that match the search term"""
        return User.objects(username__icontains=search_term)

    def get_by_id(self, model: Type[T], id: str) -> T | None:
        """fetches a document by id"""
        if not model or not id:
            return None
        return model.objects(id=id).first()

    def get_by_username(self, name: str) -> User | None:
        """fetches a user by username"""
        if name is None:
            return None
        return User.objects(username=name).first()

    def get_by_email(self, email: str) -> User | None:
        """fetches a user by email"""
        if email is None:
            return None
        return User.objects(email=email).first()

    def get_by_reset_token(self, token: str) -> User | None:
        """fetches a user by reset token"""
        if token is None:
            return None
        return User.objects(reset_token=token).first()

    def get_chats_by_user(self, user: User) -> list[Chat]:
        """
        fetches all active chats and rooms for a user

        """
        if user is None:
            return []
        return Chat.objects(Q(user_1=user.username) |
                            Q(user_2=user.username)).exclude('messages')

    def get_rooms_by_user(self, user: User) -> list[Room]:
        """
        fetches all active chats and rooms for a user

        """
        if user is None:
            return []
        return (Room.objects(members__in=[user.username])
                .exclude('messages', 'members'))

    def get_chat_by_users(self, user_1: str, user_2: str) -> Chat | None:
        """fetches a chat by the two users"""
        if user_1 is None or user_2 is None:
            return None

        variant_1 = Chat.objects(Q(user_1=user_1) & Q(user_2=user_2)).first()
        variant_2 = Chat.objects(Q(user_1=user_2) & Q(user_2=user_1)).first()

        return variant_1 or variant_2


class Cache:
    """
    a redis cache for storing session keys
    """

    settings = RedisSettings()
    HOST = settings.REDIS_HOST
    PORT = settings.REDIS_PORT
    DB = settings.REDIS_DB
    PASSWD = settings.REDIS_PASSWD
    TTL = settings.REDIS_TTL

    def __init__(self) -> None:
        if self.PASSWD:
            uri = (f'redis://:{self.PASSWD}@{self.HOST}'
                   f':{self.PORT}/{self.DB}')
        else:
            uri = f'redis://{self.HOST}:{self.PORT}/{self.DB}'

        self.redis = Redis.from_url(uri, password=self.PASSWD)

    def ping(self) -> bool:
        """checks if the cache is available"""
        return self.redis.ping()

    def get(self, key: str) -> str | None:
        """fetches a value from the cache"""
        if key is None:
            return None

        return self.redis.get(key)

    def set(self, key: str, value: str) -> None:
        """
        sets a value in the cache with a ttl
        """
        if key is None or value is None:
            return None

        self.redis.setex(key, self.TTL, value)
