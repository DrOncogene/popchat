#!usr/bin/env python3
"""
defines the room model
"""
from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    ListField,
    ReferenceField,
    EmbeddedDocumentField
)

from .model import Base
from .message import Message


class Room(Base, Document):
    """Room document model"""
    name = StringField(required=True)
    creator = ReferenceField('User')
    members = ListField(ReferenceField('User'))
    admins = ListField(ReferenceField('User'))
    messages = ListField(EmbeddedDocumentField(Message))

    def to_dict(self) -> dict:
        obj_dict = super().to_dict()
        obj_dict['members'] = [user.username for user in self.members]
        obj_dict['admins'] = [user.username for user in self.admins]

        return obj_dict

    def save(self, *args, **kwargs):
        """wrapper for document.save()"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
