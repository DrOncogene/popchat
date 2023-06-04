"""
basemodel
"""

from datetime import datetime
from bson import json_util
from mongoengine import DateTimeField


class Base:
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Create a serializable format of model.

        TODO: Find out how this class works exactly ...
        """
        obj_dict: dict = json_util.loads(self.to_json())
        obj_dict['created_at'] = obj_dict['created_at'].isoformat()
        obj_dict['updated_at'] = obj_dict['updated_at'].isoformat()
        obj_dict['id'] = str(obj_dict['_id'])

        return {k: v for k, v in obj_dict.items()
                if not k.startswith('_') and
                k not in ['password', 'reset_token']
                }
