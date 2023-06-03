#!/usr/bin/env python3
"""Messages model."""
from mongoengine import (
    EmbeddedDocument,
    StringField,
    DateTimeField,
)

from .user import User


class Message(EmbeddedDocument):
    """Message model."""
    text = StringField(required=True)
    sender = StringField(required=True)
    when = DateTimeField(required=True)

    def to_dict(self):
        """Create a serializable format of model."""
        return {
            'text': self.text,
            'sender': self.sender,
            'when': self.when.isoformat()
        }