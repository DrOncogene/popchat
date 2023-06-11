# """
# defines a set of background tasks to improve
# latency
# """
# import json
# from datetime import datetime

# from werkzeug.security import check_password_hash

# from storage import db

# def put_user(payload: dict):
#     """deletes or edit a user"""
#     print('TASK CALLED')
#     user = db.get_one('User', payload.get('username'))
#     if user is None:
#         return {'error': 'Invalid username', 'status': 404}

#     if 'username' not in payload:
#         return {'error': 'Missing username', 'status': 400}
#     if 'email' not in payload:
#         return {'error': 'Missing email', 'status': 400}
#     if 'password' not in payload:
#         return {'error': 'Missing password', 'status': 400}

#     if not check_password_hash(user.password, payload.get('password')):
#         return {'error': 'Invalid password', 'status': 400}

#     user.username = payload.get('username')
#     user.email = payload.get('email')
#     if user.save():
#         return {'updated': True, 'status': 200}

#     return {'updated': False, 'status': 204}


# def add_message(payload: dict):
#     """
#     adds a new message to a room/chat

#     :param which: the type of chat (private or a room/channel)
#         valid values are room and chat
#     :param chat_id: private chat id or room id
#     :param msg: a dict containing details
#         of the new message to add
#     Return: True is success, False otherwise
#     """
#     print('ADDING MESSAGE TO DB...')
#     which: str = payload['which']
#     chat_id: str = payload['chat_id']
#     msg: 'dict[str, str]' = payload['message']

#     if which not in ['room', 'chat']:
#         return

#     if which == 'chat':
#         chat = db.get_one('Chat', chat_id)
#     else:
#         chat = db.get_one('Room', chat_id)

#     when = msg['when']
#     when_date = (datetime.fromisoformat(when.replace('Z', '+00:00'))
#                  .astimezone())
#     messages: list = json.loads(chat.messages)

#     try:
#         last_day_messages: list = messages[-1]
#         day: str = last_day_messages[0]
#         day_date = (datetime.fromisoformat(day.replace('Z', '+00:00'))
#                     .astimezone())

#         if when_date.strftime('%Y-%m-%d') == day_date.strftime('%Y-%m-%d'):
#             last_day_messages[1].append(msg)
#         else:
#             messages.append([when, [msg]])
#     except IndexError:
#         messages.append([when, [msg]])

#     chat.messages = json.dumps(messages)
#     if not db.save():
#         return False

#     return True
