#!/usr/bin/env python3
"""
defines the chat model
"""

    
from datetime import datetime
from mongoengine import (
    Document,
    ReferenceField,
    EmbeddedDocumentField,
    ListField
)

from .model import Base
from .message import Message


class Chat(Base, Document):
    """
    Chat class
    """
    user_1 = ReferenceField('User')
    user_2 = ReferenceField('User')
    messages = ListField(EmbeddedDocumentField(Message))

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict['members'] = [self.user_1.username, self.user_2.username]
        obj_dict['messages'] = [message.to_json() for message in self.messages]

        return obj_dict

    def save(self, *args, **kwargs):
        """wrapper for document.save()"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
