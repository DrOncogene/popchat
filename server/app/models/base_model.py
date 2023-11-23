"""
basemodel
"""

from datetime import datetime

from bson import json_util
from pydantic import Field, field_serializer
from beanie import Document, before_event, Update


class Base(Document):
    """Base model"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, v: datetime) -> str:
        """
        serializes datetime fields

        :param v: datetime object
        :type v: datetime

        :return: A string representation of the datetime object
        :rtype: str
        """

        return v.isoformat()

    @before_event(Update)
    def save_update_at(self) -> None:
        self.updated_at = datetime.utcnow()
