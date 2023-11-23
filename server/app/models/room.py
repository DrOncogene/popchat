#!usr/bin/env python3

"""Defines the room model"""

from datetime import datetime, UTC

from beanie import Link, before_event, Update, SaveChanges
from pydantic import model_serializer

from app.models.base_model import Base
from app.models.message import Message
from app.models.user import User
from app.utils import group_messages


class Room(Base):
    """
    Represents a Room instance.
    Rooms can contain two or more users
    """

    name: str
    creator: Link[User]
    members: list[Link[User]]
    admins: list[Link[User]]
    messages: list[Link[Message]]
    last_msg: Link[Message] | None = None
    is_deleted: bool = False

    @before_event(SaveChanges, Update)
    async def update_last_msg(self):
        """
        Updates the last_msg attribute of the chat
        """

        self.updated_at = datetime.now(UTC)
        if len(self.messages) == 0:
            return

        self.last_msg = self.messages[-1]

    @model_serializer
    def serialize_room(self) -> dict:
        """
        Serializes the room
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'creator': self.creator.username,
            'members': [member.username for member in self.members],
            'admins': [admin.username for admin in self.admins],
            'messages': group_messages(self.messages),
            'last_msg': self.last_msg,
            'type': 'room',
            'created_at': f'{self.created_at.isoformat()}Z',
            'updated_at': f'{self.created_at.isoformat()}Z',
        }

    class Settings:
        name = 'rooms'
        use_state_management = True
