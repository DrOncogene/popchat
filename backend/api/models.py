#!/usr/bin/env python3
"""Pydantic Models for the API."""
import re

from pydantic import BaseModel, EmailStr, Field


username_regex = "^[A-Za-z][A-Za-z0-9]{4,10}$"
passwd_regex = ("^(?=.*[A-Za-z])"
                "(?=.*\d)"
                "[A-Za-z\d\.+-=#_%|&@]{7,16}$")


class UserBase(BaseModel):
    """user model for the api"""
    username: str | None = Field(regex=username_regex)
    email: EmailStr | None


class UserIn(UserBase):
    """user model for the api"""
    password: str = Field(regex=passwd_regex)


class UserOut(UserBase):
    """user model for the api"""
    id: str
    auth_token: str


class Message(BaseModel):
    """message model for the api"""
    sender: str
    text: str
    when: str

class Chat(BaseModel):
    """chat model for the api"""
    id: str
    name: str
    members: list[UserOut]
    messages: list[Message]

class ApiRoom(BaseModel):
    """room model for the api"""
    id: str
    name: str
    members: list[UserOut]
    admins: list[UserOut]
    creator: UserOut
    messages: list[Message]
