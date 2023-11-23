"""
chat events
"""
from beanie import PydanticObjectId
from fastapi import BackgroundTasks

from app import sio
from app.models.user import User
from app.models.chat import Chat
from app.models.room import Room
from app.models.message import Message
from app.middlewares.chat import (
    users_search,
    fetch_user_by_id_or_username,
    fetch_user_chats,
    add_message,
    new_room,
    new_chat,
    add_or_remove_members,
    add_or_remove_admin,
    change_room_name,
    exit_room_middleware,
    purge_room,
)
from app.schemas.models import ResponseModel
from app.db import SOCKETIO_CACHE


@sio.on('connect')
async def connect(sid: str, environ: dict, auth: dict) -> bool:
    """
    handles the connection event and adds the user
    to the appropriate rooms and chats using the
    `chat.id or room.id` as the room/chat name

    :param auth: Authentication dict
        passed by the client
    """

    if auth is None:
        return False

    user_id = auth.get('id')
    if user_id is None:
        return False

    user = await fetch_user_by_id_or_username(user_id)
    if user is None:
        return False

    SOCKETIO_CACHE.setv(user_id, sid)
    await sio.save_session(sid, user_id)

    chats_or_rooms = await fetch_user_chats(user)
    for chat_or_room in chats_or_rooms:
        await sio.enter_room(sid, str(chat_or_room['id']))

    print(f'{user.username} CONNECTED')
    return True


@sio.on('disconnect')
async def handle_disconnect(sid: str):
    """
    handles the disconnection event

    :param sid: The socket id of the client
    """
    user_id = await sio.get_session(sid)
    SOCKETIO_CACHE.delete(user_id)
    print('DISCONNECTED')


@sio.on('search_users')
async def get_users(sid: str, payload: dict) -> dict:
    """
    fetches a list of users whose username matches a query
    term
    """
    user_id = payload.get('id')
    term = payload.get('search_term')

    matches = await users_search(user_id, term)

    return ResponseModel(
        message='success',
        status_code=200,
        data=matches,
    ).model_dump()


@sio.on('get_user')
async def get_user(sid: str, payload: dict) -> dict:
    """
    fetches a user from the database
    """

    if not payload or len(payload) == 0:
        return ResponseModel(
            message='no username or id',
            status_code=400,
        ).model_dump()

    username_or_id = payload.get('id') or payload.get('username')

    user = await fetch_user_by_id_or_username(username_or_id)
    if user is None:
        return ResponseModel(
            message='invalid id or username',
            status_code=404,
        ).model_dump()

    return ResponseModel(
        message='success',
        status_code=200,
        data=user.model_dump(),
    ).model_dump()


@sio.on('get_user_chats')
async def get_user_chats(sid: str, payload: dict) -> dict:
    """
    fetches all active chats and rooms for a user

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return ResponseModel(
            message='no username or id',
            status_code=400,
        ).model_dump()

    username_or_id = payload.get('username') or payload.get('id')

    user = await fetch_user_by_id_or_username(username_or_id)
    if user is None:
        return ResponseModel(
            message='invalid id or username',
            status_code=404,
        ).model_dump()

    rooms_and_chats = await fetch_user_chats(user)

    return ResponseModel(
        message='success',
        status_code=200,
        data=rooms_and_chats,
    ).model_dump()


@sio.on('get_chat')
async def get_chat(sid: str, payload: dict) -> dict:
    """
    fetches a chat from the database and reformats
    the messages to be grouped by date

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return ResponseModel(
            message='no chat id',
            status_code=400,
        ).model_dump()

    chat_id = payload.get('id')

    chat = await Chat.find(
        Chat.id == PydanticObjectId(chat_id),
        fetch_links=True,
    ).first_or_none()
    if chat is None:
        return ResponseModel(
            message='invalid chat id',
            status_code=404,
        ).model_dump()

    return ResponseModel(
        message='success',
        status_code=200,
        data=chat.model_dump(),
    ).model_dump()


@sio.on('get_room')
async def get_room(sid: str, payload: dict) -> dict:
    """fetches a room from the database

    :param `sid`: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return ResponseModel(
            message='no room id',
            status_code=400,
        ).model_dump()

    room_id = payload.get('id')

    room = await Room.find(
        Room.id == PydanticObjectId(room_id),
        fetch_links=True,
    ).first_or_none()

    if room is None:
        return ResponseModel(
            message='invalid room id',
            status_code=404,
        ).model_dump()

    return ResponseModel(
        message='success',
        status_code=200,
        data=room.model_dump(),
    ).model_dump()


@sio.on('new_message')
async def new_message(sid: str, payload: dict) -> dict:
    """handles the new message event"""

    room_or_chat_id = payload.get('id')
    msg = payload.get('message')
    chat_type = payload.get('type')

    _, err = await add_message(room_or_chat_id, msg, chat_type)
    if err:
        return err.model_dump()

    # TODO: put the message on the queue for offline users after
    # diffing with the sid store for online users

    data = {'message': msg, 'id': room_or_chat_id, 'type': chat_type}
    await sio.emit('new_message', data, to=room_or_chat_id, skip_sid=sid)

    return ResponseModel(
        message='message sent successfully',
        status_code=201,
    ).model_dump()


@sio.on('join_room')
async def join_room(sid: str, payload: dict):
    """
    adds the user to a room
    """

    room_name = payload.get('name')
    if not room_name:
        return {'error': 'missing room name', 'status': 400}

    await sio.enter_room(sid, room_name)


@sio.on('leave_room')
async def leave_room(sid: str, payload: dict):
    """
    removes a user from a room
    """

    room_name = payload.get('name')
    if not room_name:
        return {'error': 'missing room name', 'status': 400}

    await sio.leave_room(sid, room_name)


@sio.on('create_room')
async def create_room(sid: str, payload: dict) -> dict:
    """
    creates a new room and adds the creator and a mandatory
    new member to the room
    """

    name: str = payload.get('name')
    creator_id: str = payload.get('creator')
    new_members: list[str] = payload.get('members')

    room, err = await new_room(name, new_members, creator_id)

    if err:
        return err.model_dump()

    await sio.enter_room(sid, str(room.id))
    await sio.emit(
        'new_room',
        ('new', {'id': str(room.id)}),
        to=room.id,
        skip_sid=sid,
    )

    return ResponseModel(
        message='room created successfully',
        status_code=201,
        data=room.model_dump(),
    ).model_dump()


@sio.on('create_chat')
async def create_chat(sid: str, payload: dict) -> dict:
    """
    creates a new chat between two users
    """

    user_1 = payload.get('creator')
    user_2 = payload.get('user_2')
    initial_message = payload.get('message')

    chat, err = await new_chat(user_1, user_2, initial_message)
    if err:
        return err.model_dump()

    await sio.enter_room(sid, str(chat.id))

    return ResponseModel(
        message='chat created successfully',
        status_code=201,
        data=chat.model_dump(),
    ).model_dump()


@sio.on('edit_room_name')
async def edit_room_name(sid: str, payload: dict) -> dict:
    """
    edits the name of a room
    """

    room_id = payload.get('id')
    new_name = payload.get('name')
    admin = payload.get('admin')

    room, err = await change_room_name(room_id, new_name, admin)
    if err:
        return err.model_dump()

    await sio.emit(
        'room_update',
        ('update', {'id': str(room.id), 'member': admin, 'name': new_name}),
        to=room_id,
        skip_sid=sid
    )

    return ResponseModel(
        message='room name changed successfully',
        status_code=200,
        data=room.model_dump(),
    ).model_dump()


@sio.on('exit_room')
async def exit_room(sid: str, payload: dict) -> dict:
    """
    handler for leave_room event
    """

    room_id = payload.get('room_id')
    user_id = payload.get('id')

    member, err = await exit_room_middleware(room_id, user_id)
    if err:
        return err.model_dump()

    await sio.leave_room(sid, room_id)
    await sio.emit(
        'leave_room',
        {'id': room_id, 'member': member},
        to=room_id,
        skip_sid=sid
    )

    return ResponseModel(
        message='successfully exited room',
        status_code=200,
    ).model_dump()


@sio.on('delete_room')
async def delete_room(sid: str, payload: dict) -> dict:
    """
    handler for delete_room event
    """

    room_id = payload.get('id')
    user_id = payload.get('user_id')

    # TODO: check if the user is the current user
    # connected using the sid

    err = await purge_room(room_id, user_id)
    if err:
        return err.model_dump()

    return ResponseModel(
        message='successfully deleted room',
        status_code=200,
    ).model_dump()

# shared handlers
sio.on('add_member', handler=add_or_remove_members)
sio.on('remove_member', handler=add_or_remove_members)
sio.on('add_admin', handler=add_or_remove_admin)
sio.on('remove_admin', handler=add_or_remove_admin)
