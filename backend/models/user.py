#!/usr/bin/env python3

"""Defines the User model"""

from datetime import datetime
from mongoengine import StringField, Document
from werkzeug.security import generate_password_hash, check_password_hash
from models.base_model import Base


class User(Base, Document):
    """Represents a User of the PopChat app

    :param username: The username of the User
    :type username: `StringField`

    :param email: The email of the User
    :type email: `StringField`

    :param password: The password of the user, hashed
    :type password: `StringField`

    TODO : What's auth_token and reset_token for ??
    """

    username = StringField(max_length=60, required=True, unique=True)
    email = StringField(max_length=60, required=True, unique=True)
    password = StringField(required=True)
    auth_token = StringField(default=None)
    reset_token = StringField(default=None)

    def set_password(self, passwd: str) -> None:
        """Hashes the password of the user"""

        self.password = generate_password_hash(passwd)

    def validate_password(self, passwd: str) -> bool:
        """Validates the password"""

        return check_password_hash(self.password, passwd)

    def to_dict(self) -> dict:
        """Create a serializable format of `User` object.

        Password attribute is removed from the dict.

        :return: A dict with the attributes of the User.
        :rtype: dict
        """

        obj_dict = super().to_dict()

        return obj_dict

    def save(self, *args, **kwargs):
        """Save the User object to the database.

        Calls `Document.save()` function of superclass.
        `updated_at` value is updated to current time before calling save
        function.
        """

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
