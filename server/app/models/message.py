#!/usr/bin/env python3
"""Defines the Message model"""

from datetime import datetime

from beanie import Document
from pydantic import field_serializer, field_validator, model_serializer


class Message(Document):
    """
    Represents a message sent by a User.
    """

    text: str
    sender: str
    when: datetime

    @field_validator('when', mode='before', check_fields=True)
    def validate_when(cls, v: datetime) -> datetime:
        """validates the when field"""
        if type(v) is str:
            return datetime.fromisoformat(v)

        return v

    @model_serializer
    def serialize_message(self) -> dict:
        """serializes the message"""
        return {
            'id': str(self.id),
            'text': self.text,
            'sender': self.sender,
            'when': f'{self.when.isoformat()}Z',
        }

    class Settings:
        name = 'messages'
