#!/usr/bin/env python3
"""
Defines the User model
"""

from beanie import Indexed
from pydantic import model_serializer
import pymongo

from app.models.base_model import Base


class User(Base):
    """
    Represents a User of the PopChat app
    """
    username: str = Indexed(str, unique=True, index_type=pymongo.TEXT)
    email: str = Indexed(str, unique=True, index_type=pymongo.TEXT)
    password: str
    reset_token: str | None = None

    @model_serializer
    def serialize(self) -> dict:
        """
        serializes user object

        :return: A dict with the attributes.
        """

        return {
            'username': self.username,
            'email': self.email,
            'id': str(self.id)
        }

    class Settings:
        name = 'users'
