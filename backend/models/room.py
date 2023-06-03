#!usr/bin/env python3

"""Defines the room model"""

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    ListField,
    ReferenceField,
    EmbeddedDocumentField
)
from models.base_model import Base
from models.message import Message


class Room(Base, Document):
    """Represents a Chat Room instance.

    Chat Rooms can contain two Users or more.

    ==========
    Attributes
    ==========

    :param name: Name of the Chat Room.
    :type name: `StringField`

    :param creator: The creator of the Room. Is an admin by default.
    :type creator: `ReferenceField` to `User` class.

    :param members: Users who are part of the Chat Room.
    :type members: List of `User` instances

    :param admins: Users who are administrators of the Chat Room.
    :type admins: List of `User` instances.

    :param messages: Messages sent to the Chat Room.
    :type messages: List of `Message` class instances.
    """

    name = StringField(required=True)
    creator = ReferenceField('User')
    members = ListField(ReferenceField('User'))
    admins = ListField(ReferenceField('User'))
    messages = ListField(EmbeddedDocumentField(Message))

    def to_dict(self) -> dict:
        """Create a serializable format of `Room` object

        :return: A dict with the attributes of the class.
        :rtype: dict
        """

        obj_dict = super().to_dict()
        obj_dict['members'] = [user.username for user in self.members]
        obj_dict['admins'] = [user.username for user in self.admins]

        return obj_dict

    def save(self, *args, **kwargs):
        """Save the `Room` object to the database

        Calls `Document.save()` function of superclass.
        `updated_at` value is updated to current time before calling save
        function.
        """

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
