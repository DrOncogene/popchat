#!/usr/bin/env python3
"""Defines the Chat model"""

from datetime import datetime, UTC

from beanie import Link, before_event, Update, SaveChanges
from pydantic import model_serializer

from app.models.base_model import Base
from app.models.message import Message
from app.models.user import User
from app.utils import group_messages


class Chat(Base):
    """
    Represents a chat instance between two users.
    """

    user_1: Link[User]
    user_2: Link[User]
    messages: list[Link[Message]]
    last_msg: Link[Message] | None = None
    is_deleted: bool = False

    @before_event(SaveChanges, Update)
    def update_last_msg(self):
        """
        Updates the last_msg attribute of the chat
        """

        self.updated_at = datetime.now(UTC)
        if len(self.messages) == 0:
            return

        self.last_msg = self.messages[-1]

    @model_serializer
    def serialize_chat(self) -> dict:
        """
        Serializes the chat
        """
        return {
            'id': str(self.id),
            'user_1': self.user_1.username,
            'user_2': self.user_2.username,
            'last_msg': self.last_msg,
            'messages': group_messages(self.messages),
            'type': 'chat',
            'members': [self.user_1.username, self.user_2.username],
            'created_at': f'{self.created_at.isoformat()}Z',
            'updated_at': f'{self.created_at.isoformat()}Z',
        }

    class Settings:
        name = 'chats'
        use_state_management = True
