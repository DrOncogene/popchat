#!/usr/bin/env python3

"""Defines the Chat model"""

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    EmbeddedDocumentListField,
    EmbeddedDocumentField,
    QuerySet,
    queryset_manager,
)
from models.base_model import Base
from models.message import Message


class Chat(Base, Document):
    """Represents a chat instance between two users.

    :param user_1: Arbitrary first participant of the chat
    :type user_1: `ReferenceField` - Reference link to `User` class

    :param user_1: Arbitrary second participant of the chat
    :type user_2: `ReferenceField` - Reference link to `User` class

    :param messages: The content of the chat between the users.
    :type messages:
    """

    user_1 = StringField()
    user_2 = StringField()
    messages = EmbeddedDocumentListField(Message)
    last_msg = EmbeddedDocumentField(Message)

    def to_dict(self) -> dict:
        """Create a serializable format of `Chat` object

        :return: A dict with the attributes.
        :rtype: dict
        """

        obj_dict = super().to_dict()

        if self.messages:
            self.messages.sort(key=lambda a: a.when)
            obj_dict['messages'] = [message.to_dict() for message
                                    in self.messages]
        if self.last_msg:
            obj_dict['last_msg'] = self.last_msg.to_dict()

        obj_dict['type'] = 'chat'

        return obj_dict

    def save(self, *args, **kwargs):
        """Save the chat object to the database

        Calls `Document.save()` function of superclass.
        `updated_at` value is updated to current time before calling save
        function.
        """

        self.updated_at = datetime.utcnow()
        self.last_msg = self.messages[-1] if len(self.messages) > 0 else None
        return super().save(*args, **kwargs)
