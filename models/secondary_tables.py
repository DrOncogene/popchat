"""
defines secondary tables for
many-to-many relationships
"""
from sqlalchemy import Column, String, Table, ForeignKey

from .model import Base


user_chats = Table('user_chats', Base.metadata,
                    Column('user_id', String(60),
                            ForeignKey('users.id', ondelete='CASCADE'),
                            nullable=False),
                    Column('chat_id', String(60),
                            ForeignKey('chats.id', ondelete='CASCADE'),
                            nullable=False)
            )


user_rooms = Table('user_rooms', Base.metadata,
                    Column('user_id', String(60),
                            ForeignKey('users.id', ondelete='CASCADE'),
                            nullable=False),
                    Column('room_id', String(60),
                            ForeignKey('rooms.id', ondelete='CASCADE'),
                            nullable=False)
            )

room_admins = Table('rooms_admins', Base.metadata,
                    Column('room_id', String(60),
                            ForeignKey('rooms.id', ondelete='CASCADE'),
                            nullable=False),
                    Column('user_id', String(60),
                            ForeignKey('users.id', ondelete='CASCADE'),
                            nullable=False)
            )
