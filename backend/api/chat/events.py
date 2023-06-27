"""
module for generating sockeio envent handlers
"""
from datetime import datetime

from api.sockets import sio
from storage import db
from models.user import User
from models.chat import Chat
from models.room import Room
from models.message import Message


# FLAGS
ADD_MEMBER = 10
REMOVE_MEMBER = 11
ADD_ADMIN = 20
REMOVE_ADMIN = 21


def group_messages(messages: list[dict]) -> list:
    """
    takes a list of messages and groups them by date
    """

    new_messages = []
    for message in messages:
        when = message['when']
        when_date = datetime.fromisoformat(when).date().strftime('%Y-%m-%d')
        for day in new_messages:
            day_date = day[0]
            day_messages = day[1]
            if day_date == when_date:
                day_messages.append(message)
                break
        else:
            new_messages.append([when_date, [message]])

    return new_messages


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

    user = db.get_by_id(User, user_id)
    if user is None:
        return False

    rooms = db.get_rooms_by_user(user)
    for room in rooms:
        sio.enter_room(sid, str(room.id))

    chats = db.get_chats_by_user(user)
    for chat in chats:
        sio.enter_room(sid, str(chat.id))

    print(f'{user.username} CONNECTED')
    return True


@sio.on('disconnect')
async def handle_disconnect(sid):
    """
    handles the disconnection event

    :param sid: The socket id of the client
    """
    print('DISCONNECTED')


@sio.on('get_users')
async def get_users(sid: str, payload: dict) -> dict:
    """
    fetches a list of users whose username matches a query
    term
    """
    user_id = payload.get('id')
    if user_id is None:
        return {'error': 'no user id', 'status': 400}

    user = db.get_by_id(User, user_id)
    if user is None:
        return {'error': 'invalid user id', 'status': 404}

    term = payload.get('search_term', '')
    matched_users = [user.to_dict() for user in db.match_users(term)
                     if user_id != str(user.id)]

    return {'matches': matched_users, 'status': 200}


@sio.on('get_user')
async def get_user(sid: str, payload: dict) -> dict:
    """fetches a user from the database"""

    if not payload or len(payload) == 0:
        return {'error': 'no username or id', 'status': 400}

    username = payload.get('username')
    user_id = payload.get('id')

    user = db.get_by_username(username) or db.get_by_id(User, user_id)
    if user is None:
        return {'error': 'invalid id or username', 'status': 404}

    return {'user': user.to_dict(), 'status': 200}


@sio.on('get_user_chats')
async def get_user_chats(sid: str, payload: dict) -> dict:
    """
    fetches all active chats and rooms for a user

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return {'error': 'no username or id', 'status': 400}

    username = payload.get('username')
    user_id = payload.get('id')

    user = db.get_by_username(username) or db.get_by_id(User, user_id)
    if user is None:
        return {'error': 'invalid id or username', 'status': 404}

    chats = db.get_chats_by_user(user)
    rooms = db.get_rooms_by_user(user)

    rooms_chats = sorted([*chats, *rooms], key=lambda a: a.updated_at)
    rooms_chats = [chat.to_dict() for chat in rooms_chats]

    return {'all': rooms_chats, 'status': 200}


@sio.on('get_chat')
async def get_chat(sid: str, payload: dict) -> dict:
    """
    fetches a chat from the database and reformats
    the messages to be grouped by date

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return {'error': 'no chat id', 'status': 400}

    chat_id = payload.get('id')
    chat = db.get_by_id(Chat, chat_id)
    if chat is None:
        return {'error': 'invalid chat id', 'status': 404}

    chat = chat.to_dict()
    chat['messages'] = group_messages(chat['messages'])

    return {'chat': chat, 'status': 200}

@sio.on('get_room')
async def get_room(sid: str, payload: dict) -> dict:
    """Gets a room from the database and returns it
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload sent',
            'status': 400
        }

    room_id = payload.get('id')
    room = db.get_by_id(Room, room_id)

    if not room:
        return {
            'error': 'No room found',
            'status': 404
        }

    return {
        'room': room.to_dict(),
        'status': 200
    }


@sio.on('get_room')
async def get_room(sid: str, payload: dict) -> dict:
    """
    fetches a room from the database and reformats
    the messages to be grouped by date

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return {'error': 'no room id', 'status': 400}

    room_id = payload.get('id')
    room = db.get_by_id(Room, room_id)
    if room is None:
        return {'error': 'invalid room id', 'status': 404}

    room = room.to_dict()
    room['messages'] = group_messages(room['messages'])

    return {'room': room, 'status': 200}


@sio.on('get_room')
async def get_room(sid: str, payload: dict) -> dict:
    """
    fetches a room from the database and reformats
    the messages to be grouped by date

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return {'error': 'no room id', 'status': 400}

    room_id = payload.get('id')
    room = db.get_by_id(Room, room_id)
    if room is None:
        return {'error': 'invalid room id', 'status': 404}

    room = room.to_dict()
    room['messages'] = group_messages(room['messages'])

    return {'room': room, 'status': 200}


@sio.on('get_room')
async def get_room(sid: str, payload: dict) -> dict:
    """
    fetches a room from the database and reformats
    the messages to be grouped by date

    :param sid: The socket id of the client
    :param payload: The payload sent by the client
    """

    if not payload or len(payload) == 0:
        return {'error': 'no room id', 'status': 400}

    room_id = payload.get('id')
    room = db.get_by_id(Room, room_id)
    if room is None:
        return {'error': 'invalid room id', 'status': 404}

    room = room.to_dict()
    room['messages'] = group_messages(room['messages'])

    return {'room': room, 'status': 200}


@sio.on('new_message')
async def new_message(sid: str, payload: dict) -> dict:
    """
    adds a message to a chat or room and emits
    an event to all members of the room or chat
    """

    if not payload:
        return {'error': 'invalid payload', 'status': 400}

    chat_type = payload.get('type')
    room_or_chat_id = payload.get('id')
    message = payload.get('message')
    if not chat_type or not room_or_chat_id or not message:
        return {'error': 'invalid payload', 'status': 400}

    if chat_type == 'room':
        room_or_chat = db.get_by_id(Room, room_or_chat_id)
    else:
        room_or_chat = db.get_by_id(Chat, room_or_chat_id)

    if room_or_chat is None:
        return {'error': 'invalid chat or room id', 'status': 404}

    if chat_type == 'room':
        members = room_or_chat.members
    elif chat_type == 'chat':
        members = [room_or_chat.user_1, room_or_chat.user_2]

    message = Message(**message)
    message.when = datetime.fromisoformat(message.when)
    if message.sender not in members:
        return {'error': 'user not in chat or room', 'status': 403}

    room_or_chat.update(add_to_set__messages=message)
    room_or_chat.reload()
    room_or_chat.save()

    payload = {'message': message.to_dict(), 'id': str(room_or_chat.id)}
    await sio.emit('new_message', payload,
                   to=str(room_or_chat.id), skip_sid=sid)

    return {'success': True, 'status': 201}


@sio.on('join_room')
async def join_room(sid: str, payload: dict) -> dict:
    """
    adds the user to a room
    """

    room_name = payload.get('name')
    if not room_name:
        return {'error': 'missing room name', 'status': 400}

    sio.enter_room(sid, room_name)


@sio.on('leave_room')
async def leave_room(sid: str, payload: dict) -> dict:
    """
    adds the user to a room
    """

    room_name = payload.get('name')
    if not room_name:
        return {'error': 'missing room name', 'status': 400}

    sio.leave_room(sid, room_name)


@sio.on('create_room')
async def create_room(sid: str, payload: dict) -> dict:
    """
    creates a new room and adds the creator and a mandatory
    new member to the room
    """

    name: str = payload.get('name')
    creator_id: str = payload.get('creator')
    new_members: list[str] = payload.get('members')
    if not name or not creator_id or not new_members or not len(new_members):
        return {'error': 'missing required info', 'status': 400}

    creator_in_db = db.get_by_id(User, creator_id)
    if creator_id is None:
        return {'error': 'invalid user id', 'status': 404}

    for member in new_members:
        new_member = db.get_by_username(member)
        if new_member is None:
            return {'error': 'invalid user id', 'status': 404}

    room = Room(
        name=name,
        creator=creator_in_db.username,
        members=[creator_in_db.username, *new_members],
        admins=[creator_in_db.username]
        )
    room.save()
    room.reload()

    sio.enter_room(sid, str(room.id))
    await sio.emit('new_room', {'id': str(room.id)})

    return {'room': room.to_dict(), 'status': 201}


@sio.on('create_chat')
async def create_chat(sid: str, payload: dict) -> dict:
    """
    creates a new chat between two users
    """

    user_1 = payload.get('creator')
    user_2 = payload.get('user_2')
    initial_message = payload.get('message')
    if not user_1 or not user_2 or not initial_message:
        return {'error': 'missing required info', 'status': 400}

    user_1 = db.get_by_username(user_1)
    user_2 = db.get_by_username(user_2)
    if user_1 is None or user_2 is None:
        return {'error': 'invalid user id or username', 'status': 404}

    existing_chat = db.get_chat_by_users(user_1.username, user_2.username)
    if existing_chat is not None:
        return {'error': 'chat already exists', 'status': 400}

    message = Message(**initial_message)
    message['when'] = datetime.fromisoformat(message['when'])
    chat = Chat(
        user_1=user_1.username,
        user_2=user_2.username,
        messages=[message]
        )
    chat.save()
    chat.reload()

    sio.enter_room(sid, str(chat.id))
    await sio.emit('new_chat', {'id': str(chat.id)})

    chat_dict = chat.to_dict()
    chat_dict['messages'] = group_messages(chat_dict['messages'])

    return {'chat': chat_dict, 'status': 201}


async def add_or_remove_member(sid: str, payload: dict) -> dict:
    """
    adds a member to a room
    """

    room_id = payload.get('id')
    member = payload.get('member')
    admin = payload.get('admin')
    flag = payload.get('flag')

    if not room_id or not member or not admin or flag is None:
        return {'error': 'missing required info', 'status': 400}

    room = db.get_by_id(Room, room_id)
    if room is None:
        return {'error': 'invalid room id', 'status': 404}

    if member in room.members and flag == 1:
        return {'error': 'user already in room', 'status': 409}

    member_in_db = db.get_by_username(member)
    if member_in_db is None:
        return {'error': 'invalid username', 'status': 404}

    if admin not in room.admins:
        return {'error': 'not an admin', 'status': 403}

    if int(flag) == ADD_MEMBER:
        room.update(add_to_set__members=member_in_db.username)
    elif int(flag) == REMOVE_MEMBER:
        room.update(pull__members=member_in_db.username)
        if member_in_db.username in room.admins:
            room.update(pull__admins=member_in_db.username)
    else:
        return {'error': 'invalid flag', 'status': 400}

    room.save()
    room.reload()

    room_dict = room.to_dict()
    room_dict['messages'] = group_messages(room_dict['messages'])

    if int(flag) == ADD_MEMBER:
        await sio.emit('new_room', {'id': str(room.id)})
    elif int(flag) == REMOVE_MEMBER:
        await sio.emit('remove_from_room', {'id': str(room.id)})

    return {'room': room_dict, 'status': 201}


# both share the same handler
sio.on('add_member', add_or_remove_member)
sio.on('remove_member', add_or_remove_member)


@sio.on('edit_room_name')
async def edit_room_name(sid: str, payload: dict) -> dict:
    """
    edits the name of a room
    """

    room_id = payload.get('id')
    new_name = payload.get('name')
    admin = payload.get('admin')

    if not room_id or not new_name or not admin:
        return {'error': 'missing required info', 'status': 400}

    room = db.get_by_id(Room, room_id)
    if room is None:
        return {'error': 'invalid room id', 'status': 404}

    admin_in_db = db.get_by_username(admin)
    if admin not in room.admins or admin_in_db is None:
        return {'error': 'not an admin', 'status': 403}

    room.update(name=new_name)
    room.save()
    room.reload()

    room_dict = room.to_dict()
    room_dict['messages'] = group_messages(room_dict['messages'])

    await sio.emit('new_room', {'id': str(room.id)})

    return {'room': room_dict, 'status': 201}


# TODO: add a handler for editing the room admins list
async def add_or_remove_admin(sid: str, payload: dict) -> dict:
    """
    adds or removes an admin from the room admins list
    """
    raise NotImplementedError


sio.on('add_admin', add_or_remove_admin)
sio.on('remove_admin', add_or_remove_admin)
