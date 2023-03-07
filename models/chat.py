"""
defines the chat model
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .model import Base, Model
from .secondary_tables import user_chats


class Chat(Model, Base):
    """Chat class"""
    __tablename__ = 'chats'

    user_1 = Column(String(60), ForeignKey('users.id'), nullable=False)
    user_2 = Column(String(60), ForeignKey('users.id'), nullable=False)
    messages = Column(Text, nullable=False, default='[]')

    members = relationship('User', secondary=user_chats, back_populates='chats')

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict['members'] = [user.username for user in self.members]

        return obj_dict
