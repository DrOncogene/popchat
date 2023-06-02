"""
basemodel
"""
# from datetime import datetime
# from uuid import uuid4

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, String, TIMESTAMP, text
# from sqlalchemy.schema import FetchedValue
# from sqlalchemy.sql import func

# Base = declarative_base()


# class Model:
#     """base model class"""
#     id = Column(String(60), primary_key=True, nullable=False)
#     created_at = Column(
#         TIMESTAMP,
#         nullable=False,
#         server_default=func.now()
#     )
#     updated_at = Column(
#         TIMESTAMP,
#         nullable=False,
#         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
#         server_onupdate=FetchedValue()
#     )

#     def __init__(self, **kwargs) -> None:
#         from storage import db
#         self.id = str(uuid4())
#         self.__dict__.update(kwargs)
#         print(self.id, self.__dict__)
#         db.add(self)

#     def save(self):
#         """a wrapper for storage save"""
#         from storage import db
#         return db.save()

#     def delete(self):
#         """wrapper for storage delete"""
#         from storage import db
#         db.delete(self)

#     def to_dict(self):
#         """create a serializable format of model"""
#         from storage import db
#         obj_dict = {}
#         obj = db.get_one(type(self), self.id)
#         obj_dict.update(obj.__dict__)
#         obj_dict["created_at"] = obj_dict["created_at"].isoformat()
#         obj_dict["updated_at"] = obj_dict["updated_at"].isoformat()

#         obj_dict.pop('_sa_instance_state', None)
#         obj_dict.pop('password', None)

#         return obj_dict

from datetime import datetime
from bson import json_util
from mongoengine import DateTimeField


class Base:
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # meta = {'allow_inheritance': True}

    def to_dict(self) -> dict:
        """Create a serializable format of model.

        TODO: Find out how this class works exactly ...
        """
        obj_dict: dict = json_util.loads(self.to_json())
        obj_dict['created_at'] = obj_dict['created_at'].isoformat()
        obj_dict['updated_at'] = obj_dict['updated_at'].isoformat()
        obj_dict['id'] = str(obj_dict['_id'])
        obj_dict.update({k: v for k, v in obj_dict.items()
                         if not k.startswith('_') and
                         k not in ['created_at', 'updated_at']})

        return obj_dict
