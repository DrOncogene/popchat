"""
api endpoints
"""
from flask import jsonify, request, abort
from flask_login import current_user
from werkzeug.security import generate_password_hash

from storage import db
from models.room import Room
from models.chat import Chat
from . import api_v1


@api_v1.get('/users', strict_slashes=False)
def get_users():
    """fetches all users"""
    all_users = db.get_all('User')
    print(current_user)
    return jsonify([user.to_dict() for user in all_users])

@api_v1.get('/users/<user_id>')
def get_user(user_id):
    """fetches a user"""
    user = db.get_one('User', user_id)
    if user is None:
        return jsonify({'error': 'user not found'}), 404

    return jsonify(user.to_dict())

@api_v1.route('/users/<user_id>', methods=['DELETE', 'PUT'],
                strict_slashes=False)
def edit_user(user_id):
    """deletes or edit a user"""
    user = db.get_one('User', user_id)
    if user is None:
        return jsonify({'error': 'user not found'}), 404

    if request.method == 'DELETE':
        db.delete(user)
        if not db.save():
            return jsonify({'error': 'account deletion failed'}), 204

        return jsonify('user deleted')

    if request.method == 'PUT':
        data = request.get_json(silent=True)
        if data is None:
            abort(400)

        if 'username' not in data:
            return jsonify({'error': 'Missing username'}), 400
        if 'email' not in data:
            return jsonify({'error': 'Missing email'}), 400
        if 'password' not in data:
            return jsonify({'error': 'Missing password'}), 400

        user.username = data['username']
        user.email = data['email']
        user.password = generate_password_hash(data['password'])
        if user.save():
            return jsonify({'updated': True})
        else:
            return jsonify({'updated': False}), 204

@api_v1.get('/users/<user_id>/<chat_type>', strict_slashes=False)
def get_chats(user_id, chat_type):
    """fetches the rooms or chats for a user"""
    user = db.get_one('User', user_id)
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    if chat_type == 'rooms':
        return jsonify([room.to_dict() for room in user.rooms])
    if chat_type == 'chats':
        return jsonify([chat.to_dict() for chat in user.chats])

@api_v1.post('/rooms/new', strict_slashes=False)
def create_room():
    """creates a new room and set the admin"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400)

    if 'name' not in data:
        return jsonify({'error': 'missing room name'}), 400

    room = Room(**data)

    creator = current_user
    room.created_by = current_user.id

    creator.rooms.append(room)
    room.admins.append(creator)
    db.save()

    return jsonify(room.to_dict()), 201

@api_v1.post('/chats/new', strict_slashes=False)
def create_chat():
    """creates a new room and set the admin"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400)

    if 'user_2' not in data:
        return jsonify({'error': 'missing receiver id'}), 400

    chat = Chat(**data)

    user_2 = db.get_one('User', data['user_2'])
    if user_2 is None:
        return jsonify({'error': 'invalid username'}), 404

    chat.user_1 = current_user.id
    chat.user_2 = user_2.id
    current_user.chats.append(chat)
    user_2.chats.append(chat)
    db.save()

    return jsonify(chat.to_dict()), 201

@api_v1.post('/rooms/<room_id>/add/<user_id>', strict_slashes=False)
def room_add_user(room_id, user_id):
    """adds a user to a room"""
    user = db.get_one('User', user_id)
    if user is None:
        return jsonify({'error': 'user not found'}), 404

    room = db.get_one('Room', room_id)
    if room is None:
        return jsonify({'error': 'invalid room id'}), 404

    user.rooms.append(room)
    db.save()

    return jsonify(user.to_dict())
