#!/usr/bin/env python3
"""
defines the chat model
"""

    
from datetime import datetime
from mongoengine import (
    Document,
    ReferenceField,
    EmbeddedDocumentListField,
    EmbeddedDocumentField,
    QuerySet,
    queryset_manager,
)

from .model import Base
from .message import Message


class Chat(Base, Document):
    """
    Chat class
    """
    user_1 = ReferenceField('User')
    user_2 = ReferenceField('User')
    messages = EmbeddedDocumentListField(Message)
    last_msg = EmbeddedDocumentField(Message)


    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict['user_1'] = self.user_1.username
        obj_dict['user_2'] = self.user_2.username

        if self.messages:
            self.messages.sort(key=lambda a: a.when)
            obj_dict['messages'] = [message.to_dict() for message
                                    in self.messages]
        if self.last_msg:
            obj_dict['last_msg'] = self.last_msg.to_dict()

        obj_dict['type'] = 'chat'

        return obj_dict

    def save(self, *args, **kwargs):
        """wrapper for document.save()"""
        self.updated_at = datetime.utcnow()
        self.last_msg = self.messages[-1] if self.messages else None
        return super().save(*args, **kwargs)
