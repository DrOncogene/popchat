"""
the storage engine
"""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.model import Base
from models.user import User
from models.chat import Chat
from models.room import Room


class Engine:
    """db engine"""
    __classes = {
        'User': User,
        'Chat': Chat,
        'Room': Room
    }

    def __init__(self) -> None:
        user = getenv('DB_USER', 'popchat_dev')
        passwd = getenv('DB_PWD', 'popchat_pwd')
        host = getenv('DB_HOST', 'localhost')
        port = getenv('DB_PORT', '3306')
        db_name = getenv('DB_NAME', 'popchat_dev_db')
        self.__engine = create_engine(
            f"mysql+mysqldb://{user}:{passwd}@{host}:{port}/{db_name}",
            pool_pre_ping=True
        )
        self.__session = None
        self.__sessionmaker = None

    def load(self):
        """connects and loads the db"""
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine,
                                expire_on_commit=False, autoflush=False)
        self.__sessionmaker = scoped_session(factory)
        self.__session = self.__sessionmaker()

    def get_one(self, cls, obj_id: str):
        """fetches a single item by id or username"""
        session = self.__session
        if isinstance(cls, str):
            cls = self.__classes[cls]
        if cls is User:
            obj = (session.query(cls).filter_by(username=obj_id).first() or
                    session.query(cls).filter_by(id=obj_id).first())
        else:
            obj = session.query(cls).filter_by(id=obj_id).first()

        return obj

    def get_all(self, cls) -> list:
        """fetches all items"""
        if cls is None:
            return []

        if isinstance(cls, str):
            cls = self.__classes[cls]

        return self.__session.query(cls).all()

    def add(self, obj):
        """add a new obj to the session"""
        self.__session.add(obj)

    def save(self) -> bool:
        """persist the current session to db"""
        try:
            self.__session.commit()
            return True
        except Exception as err:
            self.__session.rollback()
            print(err)
            return False

    def delete(self, obj):
        """ deletes obj from the current session"""
        if obj is not None:
            self.__session.delete(obj)

    def close(self):
        """
        closes the current session and creates
        a new one in order to release resources
        """
        self.__session.close()
        self.__session = self.__sessionmaker()
