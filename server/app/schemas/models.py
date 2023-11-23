#!/usr/bin/env python3
"""
Pydantic Models for the API.
"""
from datetime import datetime
import re
from typing import Any

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
    AliasChoices
)
from pydantic_core import PydanticCustomError


class UserBase(BaseModel):
    """base user schema"""
    username: str | None = None
    email: EmailStr | None = None

    @field_validator('username', mode='before')
    @classmethod
    def validate_username(cls, v: str):
        """validates username"""

        USERNAME_REGEX = "^[A-Za-z][A-Za-z0-9]{4,10}$"
        matches = re.fullmatch(USERNAME_REGEX, v)

        if matches is None:
            raise PydanticCustomError(
                'username_validation_error',
                'username must start with a letter and'
                ' be between 4 and 10 characters long'
            )

        return v

    @field_validator('password', check_fields=False, mode='before')
    @classmethod
    def validate_password(cls, v: str):
        """validates password"""

        PASSWD_REGEX = (
            "^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)"  # noqa: W605
            "[A-Za-z\d\.+-=#_%|&@]{7,16}$"
        )  # noqa: W605
        if not re.fullmatch(PASSWD_REGEX, v):
            raise PydanticCustomError(
                'password_validation_error',
                'password must be between 7 and 16 characters long'
                ' and contain at least one uppercase, one lowercase,'
                ' one number and one of special character in .+-=#_%|&@'
            )

        return v


class UserRegister(UserBase):
    """user registration schema"""
    username: str
    email: EmailStr
    password: str


class UserLogin(UserBase):
    """user input schema"""
    password: str


class UserOut(UserBase):
    """user return schema"""
    id: str = Field(validation_alias=AliasChoices('_id', 'id'))


class MessageSchema(BaseModel):
    """Schema model for the api"""
    id: str | None = Field(validation_alias=AliasChoices('_id', 'id'))
    sender: str
    text: str
    when: datetime

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v: Any) -> str:
        """validates the id field"""
        return str(v)

    @field_serializer('when')
    def serialize_when(self, v: datetime) -> str:
        """serializes the when field"""
        return v.isoformat() + 'Z'


class DayMessages(BaseModel):
    """schema for messages grouped by day"""
    date: str
    messages: list[MessageSchema]

    @model_serializer
    def serialize_day_messages(self) -> dict:
        """serializes the day messages"""
        return {
            'date': self.date,
            'messages': [message.model_dump() for message in self.messages],
        }


class GenericChat(BaseModel):
    """base class for chat and room schemas"""
    id: str = Field(validation_alias=AliasChoices('_id', 'id'))
    last_msg: MessageSchema | None
    updated_at: datetime | None = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v: Any) -> str:
        """validates the id field"""
        return str(v)

    @field_serializer('updated_at', when_used='unless-none')
    def serialize_updated_at(self, v: datetime) -> str:
        """serializes the updated_at field"""
        return v.isoformat() + 'Z'


class ChatSchema(GenericChat):
    """chat model for the api"""
    user_1: str
    user_2: str
    type: str = 'chat'

    @field_validator('user_1', 'user_2', mode='before')
    @classmethod
    def validate_users(cls, v: str | dict) -> str:
        """validates the users field"""
        if isinstance(v, dict):
            assert v.get('username'), 'user must have a username field'
            return v.get('username')

        return v


class ChatWithMessages(ChatSchema):
    """chat model for the api with messages"""
    members: list[str] | None = None
    messages: list[MessageSchema]

    @field_serializer('messages', mode='plain', when_used='unless-none')
    def serialize_messages(self, v: list[MessageSchema]) -> list[dict]:
        """serializes the messages"""
        from app.utils import group_messages

        return group_messages(v)


class RoomSchema(GenericChat):
    """room model for the api"""
    name: str
    type: str = 'room'


class RoomWithMessages(RoomSchema):
    """
    room model for the api with messages
    """
    admins: list[str]
    creator: str
    members: list[str]
    messages: list[MessageSchema]

    @field_serializer('messages', when_used='unless-none')
    def serialize_messages(self, v: list[MessageSchema]) -> list[dict]:
        """serializes messages field"""
        from app.utils import group_messages

        return group_messages(v)


class ResponseModel(BaseModel):
    """response model for the api"""
    message: str
    status_code: int
    data: dict | list | None = None
