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
# from models.room import Room
# from .background_tasks import put_user, add_message


# @sio.on('get_users')
# def get_users():
#     """fetches all users"""
#     all_users = db.get_all('User')

#     return [user.to_dict() for user in all_users]


# @sio.on('get_user')
# def get_user(user_id: str):
#     """fetches a user"""
#     user = db.get_one('User', user_id)
#     if user is None:
#         return {'error': 'user not found', 'status': 404}

#     user_dict: dict = user.to_dict()
#     user_dict['all_chats'] = user_dict['rooms'] + user_dict['chats']
#     user_dict['all_chats']\
#         .sort(key=lambda x: datetime.fromisoformat(x['updated_at']),
#               reverse=True)

#     return user_dict


# @sio.on('edit_user')
# def edit_user(payload: dict):
#     """deletes or edit a user"""
#     sio.start_background_task(put_user, payload)


# @sio.on('get_chat')
# def get_chat(payload: dict):
#     """fetches the rooms or chats for a user"""
#     chat_id = payload.get('id')
#     chat_type = payload.get('type')

#     if chat_id is None:
#         return

#     if chat_type == 'room':
#         room: dict = db.get_one('Room', chat_id).to_dict()
#         room['messages'] = json.loads(room['messages'])
#         room['type'] = 'room'
#         return room
#     if chat_type == 'chat':
#         chat: Chat = db.get_one('Chat', chat_id)
#         resp = chat.to_dict()
#         resp['messages'] = json.loads(resp['messages'])
#         resp['type'] = 'chat'
#         return resp


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


# def handle_chat(payload):
#     """
#     sends a message to the appropriate room

#     :param payload: The message sent by the client
#     """
#     message = payload['message']
#     chat_id = payload['chat_id']
#     data = {
#         'message': message,
#         'chat_id': chat_id
#     }
#     emit('message', data, to=chat_id, include_self=False)
#     sio.start_background_task(add_message, payload)


# @sio.on('load_handlers')
# def load_handlers(user: dict):
#     """
#     load all handlers for a newly connected user

#     :param user: The dictionary containing the user data
#     """
#     join_room(user.get('username'))
#     for room in user['rooms']:
#         join_room(room['id'])
#         sio.on_event('message', handle_chat)

#     for chat in user['chats']:
#         join_room(chat['id'])
#         sio.on_event('message', handle_chat)


@sio.on('connect')
async def handle_connect(sid, msg):
    """
    handles the connection event

    :param auth: Authentication dict
        passed by the client
    """
    # load_handlers(payload.get('user'))
    print('CONNECTED')


@sio.on('disconnect')
def handle_disconnect(sid):
    """
    handles the disconnection event

    :param sid: The socket id of the client
    """
    print('DISCONNECTED')


@sio.on('get_user')
def get_user(sid: str, payload: dict) -> dict:
    """fetches a user from the database"""

    if not payload or len(payload) == 0:
        return {'error': 'no username or id', 'status': 400}

    username = payload.get('username')
    user_id = payload.get('id')

    user = db.get_by_username(username) or db.get_by_id(user_id)
    if user is None:
        return {'error': 'invalid id or username', 'status': 404}

    return {'user': user.to_dict(), 'status': 200}


@sio.on('get_user_chats')
def get_user_chats(sid: str, payload: dict) -> dict:
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
def get_chat(sid: str, payload: dict) -> dict:
    """
    fetches a chat from the database

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
