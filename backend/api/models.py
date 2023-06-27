#!/usr/bin/env python3
"""Models for the API."""
import re

from pydantic import BaseModel, EmailStr, Field


username_regex = "^[A-Za-z][A-Za-z0-9]{4,10}$"  # noqa: W605
passwd_regex = ("^(?=.*[A-Za-z])"
                "(?=.*\d)"  # noqa: W605
                "[A-Za-z\d\.+-=#_%|&@]{7,16}$")  # noqa: W605


class UserBase(BaseModel):
    """user model for the api"""
    id: str | None = None
    username: str | None = Field(regex=username_regex)
    email: EmailStr | None


class UserIn(UserBase):
    """user model for the api"""
    password: str = Field(regex=passwd_regex)


class Message(BaseModel):
    """message model for the api"""
    sender: str
    text: str
    when: str


class Chat(BaseModel):
    """chat model for the api"""
    id: str
    name: str
    members: list[UserBase]
    messages: list[Message]


class ApiRoom(BaseModel):
    """room model for the api"""
    id: str
    name: str
    members: list[UserBase]
    admins: list[UserBase]
    creator: UserBase
    messages: list[Message]
