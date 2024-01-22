"""
chat middlewares
"""

from beanie.operators import Or, In, And, RegEx, AddToSet, Pull
from beanie import PydanticObjectId
from enum import Enum

from app import sio
from app.models.user import User
from app.models.room import Room
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.models import (
    ResponseModel,
    MessageSchema,
    ChatSchema,
    RoomSchema,
)
from app.db import SOCKETIO_CACHE


# ROOM OPERATION FLAGS
ADD_MEMBER = 10
REMOVE_MEMBER = 11
ADD_ADMIN = 20
REMOVE_ADMIN = 21


class Ops(Enum):
    ADD_MEMBER = 10
    RM_MEMBER = 11
    ADD_ADMIN = 20
    RM_ADMIN = 21

    @classmethod
    def is_admin(cls, value: int) -> bool:
        """checks if the flag is an admin flag"""
        return value in [cls.ADD_ADMIN, cls.RM_ADMIN]

    @classmethod
    def is_member(cls, value: int) -> bool:
        """checks if the flag is a member flag"""
        return value in [cls.ADD_MEMBER, cls.RM_MEMBER]


async def users_search(user_id: str, term: str) -> list[dict]:
    """
    searches the users collection and return a list
    of matches

    :param user_id: the id of the user making the request
    :param term: the search term
    :return list matching user objects
    """
    if not term or not user_id:
        return []

    matches = (
        await User.find(
            RegEx(User.username, term),
            User.id != PydanticObjectId(user_id),
        )
        .sort(+User.username)
        .to_list()
    )

    return [user.model_dump() for user in matches]


async def fetch_user_by_id_or_username(user_id: str) -> User | None:
    """
    fetches a user by id or username

    :param user_id: the id or username of the user
    :return the user object
    """
    if user_id is None:
        return None

    is_object_id = PydanticObjectId.is_valid(user_id)

    if is_object_id:
        user_id = PydanticObjectId(user_id)
        user = await User.find(User.id == user_id).first_or_none()
    else:
        user = await User.find(User.username == user_id).first_or_none()

    return user


async def fetch_user_chats(user: User) -> list[dict]:
    """
    fetches a user's chats and rooms

    :param user: the user object
    :return list of chats and rooms
    """
    if user is None:
        return None

    chats = await Chat.find(
        Or(
            Chat.user_1.username == user.username,
            Chat.user_2.username == user.username,
        ),
        Chat.is_deleted == False,  # noqa E712
        projection_model=ChatSchema,
        fetch_links=True,
    ).to_list()

    rooms = await Room.find(
        Room.members.username == user.username,
        Room.is_deleted == False,  # noqa E712
        projection_model=RoomSchema,
        fetch_links=True,
    ).to_list()

    rooms_chats = sorted([*chats, *rooms], key=lambda a: a.updated_at)

    return [room_or_chat.model_dump() for room_or_chat in rooms_chats]


async def add_message(
    c_id: str,
    msg: MessageSchema,
    c_type: str,
) -> tuple[bool, ResponseModel | None]:
    """adds a new message to a room or chat

    :param c_id: id of chat or room
    :param msg: the message object
    :param c_type: chat type ('room' or 'chat')

    :returns True or False
    """

    if not c_id or not msg or not c_type:
        return ResponseModel(
            message="invalid payload",
            status_code=400,
        )

    if c_type == "room":
        cls = Room
    elif c_type == "chat":
        cls = Chat
    else:
        return False, ResponseModel(
            message="invalid chat type",
            status_code=400,
        )

    chat_or_room = await cls.find_one(cls.id == PydanticObjectId(c_id))
    if chat_or_room is None:
        return False, ResponseModel(
            message="invalid chat or room id",
            status_code=404,
        )

    message = Message(**msg)

    try:
        # TODO: do not insert message by default if all
        # members are online
        await message.insert()
        await chat_or_room.fetch_link(cls.messages)
        chat_or_room.messages.append(message)
        await chat_or_room.save_changes()
        return True, None
    except Exception as err:
        return False, ResponseModel(
            message="failed to add message",
            status_code=500,
        )


async def new_room(
    name: str,
    members: list[str],
    creator: str,
) -> tuple[Room | None, ResponseModel | None]:
    """creates a new room"""

    if not name or not creator or not members:
        return None, ResponseModel(
            message="invalid payload",
            status_code=400,
        )

    if len(members) == 0:
        return None, ResponseModel(
            message="no member(s) to be added",
            status_code=400,
        )

    members_db = await User.find(In(User.username, members)).to_list()
    if len(members_db) != len(members):
        return None, ResponseModel(
            message="invalid username(s)",
            status_code=400,
        )

    creator_db = await fetch_user_by_id_or_username(creator)
    if creator_db is None:
        return None, ResponseModel(
            message="invalid creator username",
            status_code=400,
        )

    try:
        new_room = await Room(
            name=name,
            creator=creator_db,
            members=[*members_db, creator_db],
            admins=[creator_db],
            messages=[],
        ).create()
        for member in members_db:
            member_sid = SOCKETIO_CACHE.get(str(member.id))
            if member_sid:
                await sio.enter_room(member_sid, new_room.id)

        return new_room, None
    except Exception as err:
        return None, ResponseModel(
            message="failed to create room",
            status_code=500,
        )


async def new_chat(
    user_1: str,
    user_2: str,
    msg: Message | None = None,
) -> tuple[Chat | None, ResponseModel | None]:
    """creates a new chat"""

    if not user_1 or not user_2 or not msg:
        return None, ResponseModel(
            message="invalid payload",
            status_code=400,
            data=None,
        )

    try:
        msg = await Message(**msg).create()
    except Exception as err:
        return None, ResponseModel(
            message="invalid message payload",
            status_code=400,
            data=None,
        )

    users = await User.find(
        Or(User.username == user_1, User.username == user_2)
    ).to_list()
    if len(users) != 2:
        return None, ResponseModel(
            message="invalid username(s)",
            status_code=400,
            data=None,
        )

    existing_chat = await Chat.find_one(
        Or(
            And(
                Chat.user_1.username == user_1,
                Chat.user_2.username == user_2,
            ),
            And(
                Chat.user_1.username == user_2,
                Chat.user_2.username == user_1,
            ),
        ),
    )
    if existing_chat is not None:
        return None, ResponseModel(
            message="chat already exists",
            status_code=400,
            data=None,
        )

    try:
        new_chat = await Chat(
            user_1=users[0],
            user_2=users[1],
            messages=[msg.to_ref()],
        ).create()
        await new_chat.fetch_all_links()
        user_2_sid = SOCKETIO_CACHE.get(str(users[1].id))
        if user_2_sid:
            data = {"id": str(new_chat.id), "texter": user_1}
            await sio.enter_room(user_2_sid, str(new_chat.id))
            await sio.emit("new_chat", data, to=user_2_sid)

        return new_chat, None
    except Exception as err:
        return None, ResponseModel(
            message="failed to create chat",
            status_code=500,
            data=None,
        )


async def add_or_remove_members(sid: str, payload: dict) -> dict:
    """
    adds a member to a room and sends
    a notification to the room

    :param sid: the socket id of the client
    :param payload: the payload sent by the client
    """

    room_id: str = payload.get("id")
    members: list[str] = payload.get("members")
    admin: str = payload.get("admin")

    try:
        flag = int(payload.get("flag"))
        if not Ops.is_member(flag):
            raise ValueError
    except (ValueError, TypeError):
        return ResponseModel(
            message="invalid flag",
            status_code=400,
        ).model_dump()

    if not members or not all([room_id, len(members), admin]):
        return ResponseModel(
            message="invalid payload",
            status_code=400,
        ).model_dump()

    room = await Room.find_one(Room.id == PydanticObjectId(room_id))
    if room is None:
        return ResponseModel(
            message="invalid room id",
            status_code=404,
        )

    members_in_db = [
        await fetch_user_by_id_or_username(member) for member in members
    ]
    if None in members_in_db or len(members_in_db) == 0:
        return ResponseModel(
            message="invalid member(s) username",
            status_code=404,
        ).model_dump()

    await room.fetch_link(Room.admins)
    admin_in_db = await fetch_user_by_id_or_username(admin)
    if admin_in_db not in room.admins:
        return ResponseModel(
            message="not an admin",
            status_code=403,
        ).model_dump()
    if set(members).intersection(set([ad.username for ad in room.admins])):
        return ResponseModel(
            message="cannot remove admin, revoke admin privilege first",
            status_code=403,
        ).model_dump()

    members_ref = [user.to_ref() for user in members_in_db]
    if flag == Ops.ADD_MEMBER.value:
        room = await room.update(
            AddToSet({Room.members: {"$each": members_ref}})
        )
    else:
        room = await room.update(Pull(In(Room.members, members_ref)))
        room = await room.update(Pull(In(Room.admins, members_ref)))

    await room.save_changes()
    for member in members_in_db:
        data = {
            "id": room_id,
            "member": member.username,
            "name": room.name,
            "admin": admin,
        }
        member_sid = SOCKETIO_CACHE.get(str(member.id))
        if member_sid:
            await sio.enter_room(member_sid, room_id)
        if flag == Ops.ADD_MEMBER.value:
            await sio.emit(
                "add_to_room", ("new", data), to=room_id, skip_sid=sid
            )
        else:
            await sio.emit(
                "remove_from_room", ("remove", data), to=room_id, skip_sid=sid
            )

    room = await Room.get(room.id, fetch_links=True)
    return ResponseModel(
        message="success",
        status_code=200,
        data=room.model_dump(),
    ).model_dump()


async def add_or_remove_admin(sid: str, payload: dict) -> dict:
    """grant or revoke admin status to a user

    :param sid: the socket id of the client
    :param payload: the payload sent by the client
    """

    room_id: str = payload.get("id")
    member: str = payload.get("member")
    admin: str = payload.get("admin")

    try:
        flag = int(payload.get("flag"))
        if not Ops.is_admin(flag):
            raise ValueError
    except (ValueError, TypeError):
        return ResponseModel(
            message="invalid flag",
            status_code=400,
        ).model_dump()

    if not all([room_id, member, admin]):
        return ResponseModel(
            message="invalid payload",
            status_code=400,
        ).model_dump()

    room = await Room.find_one(Room.id == PydanticObjectId(room_id))
    if room is None:
        return ResponseModel(
            message="invalid room id",
            status_code=404,
        )

    member_in_db = await fetch_user_by_id_or_username(member)
    if not member_in_db:
        return ResponseModel(
            message="invalid member username",
            status_code=404,
        ).model_dump()

    await room.fetch_link(Room.creator)
    admin_in_db = await fetch_user_by_id_or_username(admin)
    if admin_in_db != room.creator:
        return ResponseModel(
            message="not the creator",
            status_code=403,
        ).model_dump()

    data = {
        "id": room_id,
        "name": room.name,
        "member": member,
        "admin": admin,
    }
    member_ref = member_in_db.to_ref()
    if flag == ADD_ADMIN:
        room = await room.update(AddToSet({Room.admins: member_ref}))
    else:
        room = await room.update(Pull({Room.admins: member_ref}))

    await room.save_changes()
    if flag == Ops.ADD_ADMIN.value:
        await sio.emit("add_admin", ("grant", data), to=room_id, skip_sid=sid)
    else:
        await sio.emit(
            "remove_admin", ("revoke", data), to=room_id, skip_sid=sid
        )
    room = await Room.get(room.id, fetch_links=True)

    return ResponseModel(
        message="success",
        status_code=200,
        data=room.model_dump(),
    ).model_dump()


async def exit_room_middleware(
    room_id: str,
    user_id: str,
) -> tuple[str | None, ResponseModel | None]:
    """
    removes self from a room

    :param room_id: the id of the room
    :param user_id: the id of the user

    :returns the username of the user or an error
    """

    if not room_id or not user_id:
        return None, ResponseModel(
            message="invalid payload",
            status_code=400,
        )

    room = await Room.find_one(Room.id == PydanticObjectId(room_id))
    if room is None:
        return None, ResponseModel(
            message="invalid room id",
            status_code=404,
        )

    user = await fetch_user_by_id_or_username(user_id)
    member = user.username
    if user is None:
        return None, ResponseModel(
            message="invalid user id",
            status_code=404,
        )

    await room.fetch_link(Room.creator)
    if user == room.creator:
        return None, ResponseModel(
            message="creator cannot exit room, delete room instead",
            status_code=403,
        )

    await room.fetch_link(Room.members)
    if user not in room.members:
        return None, ResponseModel(
            message="user not in room",
            status_code=400,
        )

    room.members.remove(user)
    await room.save_changes()

    return member, None


async def change_room_name(
    room_id: str,
    new_name: str,
    admin: str,
) -> tuple[Room | None, ResponseModel | None]:
    """
    changes the name of a room

    :param room_id: the id of the room
    :param new_name: the new name of the room
    :param admin: username or id of the admin making the change
    """

    if not room_id or not new_name or not admin:
        return (
            None,
            ResponseModel(
                message="invalid payload",
                status_code=400,
            ).model_dump(),
        )

    room = await Room.find_one(
        Room.id == PydanticObjectId(room_id),
        fetch_links=True,
    )
    if room is None:
        return (
            None,
            ResponseModel(
                message="invalid room id",
                status_code=404,
            ).model_dump(),
        )

    admin_in_db = await fetch_user_by_id_or_username(admin)
    if admin_in_db not in room.admins:
        return (
            None,
            ResponseModel(
                message="not an admin",
                status_code=403,
            ).model_dump(),
        )

    room = await room.set({Room.name: new_name})
    await room.save_changes()

    return room, None


async def purge_room(room_id: str, user_id: str) -> ResponseModel:
    """
    deletes a room

    :param room_id: the id of the room
    :param user_id: the id of the user
    """

    if not room_id or not user_id:
        return ResponseModel(
            message="invalid payload",
            status_code=400,
        )

    room = await Room.find_one(Room.id == PydanticObjectId(room_id))
    if room is None:
        return ResponseModel(
            message="invalid room id",
            status_code=404,
        )

    user = await fetch_user_by_id_or_username(user_id)
    if user is None:
        return ResponseModel(
            message="invalid user id",
            status_code=404,
        )

    await room.fetch_link(Room.creator)
    if user != room.creator:
        return ResponseModel(
            message="cannot delete room, you are not the creator",
            status_code=403,
        )

    # await room.delete()
    room.is_deleted = True
    await room.save_changes()

    return None
