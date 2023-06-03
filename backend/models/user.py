#!/usr/bin/env python3
"""
defines the user model
"""
from datetime import datetime
from mongoengine import StringField, Document
from werkzeug.security import generate_password_hash, check_password_hash

from .model import Base


class User(Base, Document):
    """user document model"""
    username = StringField(max_length=60, required=True, unique=True)
    email = StringField(max_length=60, required=True, unique=True)
    password = StringField(required=True)
    auth_token = StringField(default=None)
    reset_token = StringField(default=None)

    def set_password(self, passwd: str):
        """hashes password"""
        self.password = generate_password_hash(passwd)

    def validate_password(self, passwd: str):
        """validates the password"""
        return check_password_hash(self.password, passwd)

    def to_dict(self) -> dict:
        """converts user to dict"""
        obj_dict = super().to_dict()

        return obj_dict
    
    def save(self, *args, **kwargs):
        """wrapper for document.save()"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
