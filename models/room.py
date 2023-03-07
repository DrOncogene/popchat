"""
defines the room model
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .model import Base, Model
from .secondary_tables import user_rooms, room_admins


class Room(Model, Base):
    """Room class"""
    __tablename__ = 'rooms'

    name = Column(String(60), nullable=False)
    created_by = Column(String(60),
                        ForeignKey('users.id', ondelete='SET NULL')
                    )
    messages = Column(Text, nullable=False, default='[]')

    members = relationship('User', secondary=user_rooms,
                                back_populates='rooms')
    admins = relationship('User', secondary=room_admins)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict['members'] = [user.username for user in self.members]
        obj_dict['admins'] = [user.username for user in self.admins]

        return obj_dict
