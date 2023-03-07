"""
defines the user model
"""
import json
from datetime import timezone

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .model import Base, Model
from .secondary_tables import user_chats, user_rooms


class User(UserMixin, Model, Base):
    """User class"""
    __tablename__ = 'users'

    username = Column(String(60), unique=True, nullable=False)
    email = Column(String(60), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    chats = relationship('Chat', secondary=user_chats, back_populates='members')
    rooms = relationship('Room', secondary=user_rooms,
                         back_populates='members')

    def set_password(self, password: str):
        """
        hashes password
        """
        self.password = generate_password_hash(password)

    def validate_password(self, passwd: str):
        """
        verifies that password is correct
        :param passwd: the given password
        return: True or False
        """
        return check_password_hash(self.password, passwd)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict['rooms'] = [
            {
                'name': room.name,
                'id': room.id,
                'last_msg': (json.loads(room.messages)[-1][1][-1]
                             if len(json.loads(room.messages)) else None),
                'updated_at': room.updated_at
                .astimezone(tz=timezone.utc).isoformat(),
                'type': 'room'
            }
            for room in self.rooms
        ]
        obj_dict['chats'] = [
            {
                'members': [user.username for user in chat.members],
                'id': chat.id,
                'last_msg': (json.loads(chat.messages)[-1][1][-1]
                             if len(json.loads(chat.messages)) else None),
                'updated_at': chat.updated_at
                .astimezone(tz=timezone.utc).isoformat(),
                'type': 'chat'
            }
            for chat in self.chats
        ]

        return obj_dict
