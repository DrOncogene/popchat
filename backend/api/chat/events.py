"""
module for generating sockeio envent handlers
"""
# import json
# from datetime import datetime

# from flask_socketio import join_room, emit

from datetime import datetime
from api.sockets import sio
from storage import db
from models.user import User
from models.chat import Chat
from models.room import Room
from models.message import Message
# from .background_tasks import put_user, add_message

CREATE_ADMIN = 10
DELETE_ADMIN = 20

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
    term: str = payload.get('search_term')
    if term is None or term == '':
        return {'error': 'no search term', 'status': 400}

    matched_users = [user.to_dict() for user in db.match_users(term)]

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
    messages = []
    for message in chat['messages']:
        when = message['when']
        when_date = datetime.fromisoformat(when).date().strftime('%Y-%m-%d')
        for day in messages:
            day_date = day[0]
            day_messages = day[1]
            if day_date == when_date:
                day_messages.append(message)
                break
        else:
            messages.append([when_date, [message]])

    chat['messages'] = messages

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

@sio.on('create_room')
async def create_room(sid: str, payload: dict) -> dict:
    """
    create_room(creator_id, name, participant_id): creates a new room object, adding creator_id to admins property and named as passed and adding one mandatory participant to the room in addition to the creator

    payload: {creator: id (string), name: string, member: id(string)}

    returns: {room: room object, status: 200}, else {error: string, status: int}
    """

    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    creator_id = payload.get('creator')
    room_name = payload.get('name')
    member_id = payload.get('members')
    if not creator_id or not room_name or not member_id:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    room = Room(**payload)
    room.members.append(creator_id)
    room.admins.append(creator_id)
    room.save()

    return {
        'room': room.to_dict(),
        'status': 200
    }

@sio.on('create_chat')
async def create_chat(sid: str, payload: dict) -> dict:
    """
    create_chat(user_1_id, user_2_id, message): creates a new chat object using
      the two participants' id after verifying their existence in the db. add
      message to the chat's messages property as the first message

    payload: {user_1: username(string), user_2: string, message: Message}

    returns: {chat: chat object, status: 200}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    user_1, user_2 = payload.get('user_1'), payload.get('user_2')
    message = payload.get('message')
    if not user_1 or not user_2 or not message:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    user1_in_db = db.get_by_username(user_1)
    if not user1_in_db:
        return {
            'error': 'user_1 not found',
            'status': 404
        }
    user2_in_db = db.get_by_username(user_2)
    if not user2_in_db:
        return {
            'error': 'user_2 not found',
            'status': 404
        }

    chat = Chat(**payload, last_message=message)
    chat.save()

    return {
        'chat': chat.to_dict(),
        'status': 200j
    }

@sio.on('update_user')
async def update_user_info(sid: str, payload: dict) -> dict:
    """
    update_user(user_obj): updates a user's email or username using the user object passed. The passed object id must be the same as the existing user's id. This route does not change the password.

    payload: {user: User}

    return {success: True, status: 201, user: updated obj}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    user_in_payload = payload.get('user')
    if not user_in_payload:
        return {
            'error': 'User object missing',
            'status': 400
        }

    user_in_db = db.get_by_id(User, user_in_payload.id)
    if not user_in_db:
        return {
            'error': 'No user found',
            'status': 400
        }

    user_in_db.username = user_in_payload.username
    user_in_db.email = user_in_payload.email
    user_in_db.save()

    return {
        'status': 201,
        'success': True,
        'user': user_in_db,
    }

@sio.on('add_message')
async def add_message(sid: str, payload: dict) -> dict:
    """
    add_message(chat_id/room_id, message): add a new message to a chat or room after verifying that the message.sender exist in the db and is a participant in the room or chat

    payload: {type:'room' | 'chat', id: room_id or chat_id, message: Message}

    return: {success: True, status: 201}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    chat_type = payload.get('type')
    chat_or_room_id = payload.get('id')
    message = payload.get('message')
    if not chat_type or not chat_or_room_id or not message:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    if chat_type == 'chat':
        chat = db.get_by_id(Chat, chat_or_room_id)
    else:
        room = db.get_by_id(Room, chat_or_room_id)

    if not room:
        return {
            'error': 'No Room found',
            'status': 404
        }
    if not chat:
        return {
            'error': 'No Chat found',
            'status': 404
        }

    sender_in_db = db.get_by_id(User, message.sender)
    if not sender_in_db:
        return {
            'error': 'No user found',
            'status': 404
        }

    if room:
        if message.sender not in room.members:
            return {
                'error': 'Sender not participant in Room',
                'status': 400
            }
        room.messages.append(message)
        room.last_msg = message
        room.save()
        return {
            'success': True,
            'status': 201,
        }
    else:
        if message.sender != chat.user_1 and message.sender != chat.user_2:
            return {
                'error': 'Sender not participant in Chat',
                'status': 400
            }
        chat.messages.append(message)
        chat.last_msg = message
        chat.save()
        return {
            'success': True,
            'status': 201,
        }
@sio.on('update_room_name')
async def update_room_name(sid: str, payload: dict) -> dict:
    """
    update_room_name(room_id, new_name, admin_id): change the name of a room making sure the user passed is an admin of the room

    payload: {id: string, new_name: string, updater: id}

    return: {success: True, status: 201}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    room_id = payload.get('id')
    new_name = payload.get('new_name')
    admin_id = payload.get('updater')
    if not room_id or not new_name or not admin_id:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    room_in_db = db.get_by_id(Room, room_id)
    if not room_in_db:
        return {
            'error': 'No Room found',
            'status': 404
        }

    if admin_id not in room_in_db.admins:
        return {
            'error': 'User not admin',
            'status': 400
        }

    room_in_db.name = new_name
    room_in_db.save()
    return {
        'success': True,
        'status': 201
    }

@sio.on('update_room_admins')
async def update_room_admins(sid: str, payload: dict) -> dict:
    """
    update_room_admins(room_id, admin_id, new_admin, flag): add or remove an admin to the list of admins of a room depending on flag(add or remove)

    payload{room_id: id (string), admin_id: id (string),
    flag: boolean ('True' |'False')}

    flag definition: 10 - Means Add new admin, 20 - Means Delete admin

    return: {success: True, status: 201}, else {error: string, status: int}
    """

    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    room_id = payload.get('room_id')
    admin_id = payload.get('admin_id')
    flag = payload.get('flag')
    if not room_id or not admin_id or not flag:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    room_in_db = db.get_by_id(Room, room_id)
    if not room_in_db:
        return {
            'error': 'No Room found',
            'status': 404
        }

    if admin_id not in room_in_db.admins:
        return {
            'error': 'User not an Admin of Room',
            'status': 400
        }

    if flag == CREATE_ADMIN:
        room_in_db.admins.append(admin_id)
        room_in_db.save()
        return {'success': True, 'status': 200}
    elif flag == DELETE_ADMIN:
        room_in_db.admins.remove(admin_id)
        room_in_db.save()
        return {'success': True, 'status': 200}
    else:
        return {
            'error': 'Invalid flag',
            'status': 400,
        }

# TODO: This should probably be in the HTTP part of server?
@sio.on('delete_user')
async def delete_user(sid: str, payload: dict) -> dict:
    """
    delete_user(user_id, password): delete a user from the db and remove them from all rooms and chats they belong to. This is meant for users to delete their account.

    payload: {id: string, password: string}

    return: {success: True, status: 201}, else {error: string, status: int}
    """

    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    user_id = payload.get('id')
    password = payload.get('password')
    if not user_id or not password:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    user_in_db = db.get_by_id(User, user_id)
    if not user_in_db:
        return {
            'error': 'No User found',
            'status': 404
        }

    if not user_in_db.validate_password(password):
        return {
            'error': 'Wrong password',
            'status': 401
        }

    user_rooms = db.get_rooms_by_user(user_in_db)
    user_chats = db.get_chats_by_user(user_in_db)

    for room in user_rooms:
        room.members.remove(user_id)
        if user_id in room.admins:
            room.admins.remove(user_id)
        room.save()

    for chat in user_chats:
        if chat.user_1 == user_id:
            del chat.user_1
            chat.save()
        else:
            del chat.user_2
            chat.save()

    user_in_db.delete()

    return {'success': True, 'status': 201}

@sio.on('delete_chat')
async def delete_chat(sid: str, payload: dict) -> dict:
    """
    delete_chat(chat_id): delete a chat for the current user by removing the current user from the chat, leaving the chat with one user

    payload: {id: string, user_id: string}

    return: {success: True, status: 201}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    chat_id = payload.get('id')
    user_id = payload.get('user_id')
    if not chat_id or not user_id:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    chat_in_db = db.get_by_id(Chat, chat_id)
    if not chat_in_db:
        return {
            'error': 'No Chat found',
            'status': 404
        }

    user_in_db = db.get_by_id(User, user_id)
    if not user_in_db:
        return {
            'error': 'No User found',
            'status': 404
        }

    if chat_in_db.user_1 == user_id:
        del chat_in_db.user_1
        chat_in_db.save()
    else:
        del chat_in_db.user_2
        chat_in_db.save()

    return {'success': True, 'status': 201}

@sio.on('delete_room')
async def delete_room(sid: str, payload: dict) -> dict:
    """
    delete_room(room_id, admin_id): deletes a room as long as the current user is an admin in the room

    payload: {room_id: string, admin_id: string}

    return: {success: True, status: 201}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    room_id = payload.get('room_id')
    admin_id = payload.get('admin_id')
    if not room_id or not admin_id:
        return {
            'error': 'Invalid payload',
            'status': 400
        }

    room_in_db = db.get_by_id(Room, room_id)
    if not room_in_db:
        return {
            'error': 'No Room found',
            'status': 404
        }

    if admin_id not in room_in_db.admins:
        return {
            'error': 'User not an admin of Room',
            'status': 400
        }

    room_in_db.delete()

    return {'success': True, 'status': 201}

# FIXME: payload must include user_id if author of message is to be verified
@sio.on('delete_message')
async def delete_message(sid: str, payload: dict) -> dict:
    """
    delete_message(message_id, chat_id/room_id): delete a message from a room or chat after verifying its existence in the room/chat and that the current user is the author.

    payload{message_id: id (string), chat_or_room_id: id (string)}

    return: {success: True, status: 201}, else {error: string, status: int}
    """
    if not payload or len(payload) == 0:
        return {
            'error': 'Empty payload',
            'status': 400
        }

    message_id = payload.get('message_id')
    chat_or_room_id = payload.get('chat_or_room_id')
    if not message_id or not chat_or_room_id:
        return {
            'error': 'Invalid Payload',
            'status': 400
        }

    chat_or_room = db.get_by_id(Room, chat_or_room_id) or \
                    db.get_by_id(Chat, chat_or_room_id)
    if not chat_or_room:
        return {
            'error': 'No Chat or Room found',
            'status': 404
        }

    messgs_by_id = [message.id  for message in chat_or_room.messages]
    if message_id not in messgs_by_id:
        return {
            'error': 'No Message found',
            'status': 404
        }

    message_index = messgs_by_id.index(message_id)
    chat_or_room.messages.pop(message_index)

    return {'success': True, 'status': 201}


# @sio.on('edit_user')
# def edit_user(payload: dict):
#     """deletes or edit a user"""
#     sio.start_background_task(put_user, payload)


# @sio.on('create_room')
# def new_room(payload: dict):
#     """creates a new room and set the admin"""
#     data: dict = payload.get('room_data')
#     if data is None or 'name' not in data or 'created_by' not in data:
#         return {'error': 'invalid room data', 'status': 400}

#     username = payload.get('member')
#     new_member = db.get_one('User', username)
#     if new_member is None:
#         return {'error': 'cannot create a room with one user', 'status': 400}

#     room = Room(**data)
#     room.members.append(new_member)

#     creator = db.get_one('User', data.get('created_by'))
#     creator.rooms.append(room)
#     room.admins.append(creator)
#     new_member.rooms.append(room)

#     if db.save():
#         room_dict = room.to_dict()
#         room_dict['messages'] = json.loads(room.messages)
#         room_dict['type'] = 'room'
#         emit('new_room', room_dict, include_self=False, to=username)
#         return {'room': room_dict, 'status': 201}

#     return {'error': 'unable to create room', 'status': 422}


# @sio.on('create_chat')
# def new_chat(payload: dict):
#     """creates a new room and set the admin"""
#     if 'members' not in payload:
#         return {'error': 'members array not sent', 'status': 400}

#     members = payload.pop('members')
#     username_1 = members[0]
#     username_2 = members[1]

#     user_2 = db.get_one('User', username_2)
#     if user_2 is None:
#         return {'error': 'invalid receiver id', 'status': 404}

#     payload.pop('id')
#     payload['messages'] = json.dumps(payload.get('messages'))
#     chat = Chat(**payload)
#     user_1 = db.get_one('User', username_1)
#     chat.user_1 = user_1.id
#     chat.user_2 = user_2.id
#     user_1.chats.append(chat)
#     user_2.chats.append(chat)

#     if db.save():
#         resp = chat.to_dict()
#         resp['messages'] = json.loads(chat.messages)
#         resp['members'] = [user.username for user in chat.members]
#         resp['type'] = 'chat'
#         emit('new_room', resp, to=user_1.username, include_self=False)
#         return {'chat': resp, 'status': 201}

#     return {'error': 'unable to create room', 'status': 422}

# # def room_add_user(room_id, user_id):
# #     """adds a user to a room"""
# #     user = db.get_one('User', user_id)
# #     if user is None:
# #         return dumps({'error': 'user not found'}), 404

# #     room = db.get_one('Room', room_id)
# #     if room is None:
# #         return dumps({'error': 'invalid room id'}), 404

# #     user.rooms.append(room)
# #     db.save()

# #     return dumps(user.to_dict())