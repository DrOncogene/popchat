#!/usr/bin/env python3

"""Defines the Message model"""

from mongoengine import (
    EmbeddedDocument,
    StringField,
    DateTimeField,
    ReferenceField
)
from models.user import User


class Message(EmbeddedDocument):
    """Represents a message sent by a User.

    :param text: The body of the message. Only string formats supported.
    :type text: StringField

    :param sender: The User who sent the message.
    :type sender: `ReferenceField` - Reference link to `User` class

    :param time_sent: The time when the message was sent
    :type time_sent: DateTimeField
    """

    text = StringField(required=True)
    sender = ReferenceField(User, required=True)
    time_sent = DateTimeField(required=True)

    def to_dict(self) -> dict:
        """Create a serializable format of Model object

        :return: A dict with the attributes.
        :rtype: dict
        """

        return {
            'text': self.text,
            'sender': self.sender,
            'time_sent': self.time_sent.isoformat()
        }
