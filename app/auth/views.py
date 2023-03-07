"""
authentication endpoints
"""
from datetime import datetime, timedelta, timezone
from os import getenv
import re

from flask import request, jsonify, abort
from flask_login import login_user, logout_user, current_user
import jwt

from storage import db
from models.user import User
from . import auth


@auth.post('/is_authenticated', strict_slashes=False)
def is_authenticated():
    """verify a user is logged in"""
    # data = request.get_json(silent=True)
    # if data is None:
    #     abort(400)

    # if 'token' not in data:
    #     return jsonify({'error': 'no token sent'}), 400

    # token = data.get('token')
    # try:
    #     payload = jwt.decode(token, key=getenv('FLASK_SECRET_KEY'),
    #                          algorithms=['HS256'])
    # except Exception:
    #     return jsonify({'error': 'invalid token'}), 401

    # user = db.get_one('User', payload.get('user_id'))
    # if user is None:
    #     return jsonify({'error': 'user not found'}), 404

    if not current_user.is_authenticated:
        return jsonify({}), 401

    user_dict: dict = current_user.to_dict()
    user_dict['all_chats'] = user_dict['rooms'] + user_dict['chats']
    user_dict['all_chats']\
        .sort(key=lambda x: datetime.fromisoformat(x['updated_at']),
              reverse=True)

    return jsonify({'user': user_dict})

@auth.post('/login', strict_slashes=False)
def login():
    """logs in the user"""
    data = request.get_json(silent=True)
    if data is None:
        abort(400)

    if 'username' not in data:
        return jsonify({'error': 'Missing username'}), 400
    if 'password' not in data:
        return jsonify({'error': 'Missing password'}), 400

    user: User = db.get_one('User', data['username'])
    if user is None:
        return jsonify({'error': 'invalid username'}), 404

    password = data['password']
    if not user.validate_password(password):
        return jsonify({'error': 'invalid password'}), 401

    if not login_user(user, remember=True):
        return jsonify({'error': 'unable to login, retry'}), 405
    # payload = {
    #     'user_id': user.id,
    #     'exp': datetime.now(tz=timezone.utc) + timedelta(hours=6.0)
    # }
    # token = jwt.encode(payload=payload, key=getenv('FLASK_SECRET_KEY'))

    user_dict: dict = user.to_dict()
    user_dict['all_chats'] = user_dict['rooms'] + user_dict['chats']
    user_dict['all_chats']\
        .sort(key=lambda x: datetime.fromisoformat(x['updated_at']),
              reverse=True)

    return jsonify({'user': user_dict})


@auth.post('/register', strict_slashes=False)
def register():
    """register a new user"""
    data: dict = request.get_json(silent=True)
    if data is None:
        abort(400)

    if 'username' not in data:
        return jsonify({'error': 'Missing username'}), 400
    if 'email' not in data:
        return jsonify({'error': 'Missing email'}), 400
    if 'password' not in data:
        return jsonify({'error': 'Missing password'}), 400

    if not validate_inputs(data['username'], 1):
        return jsonify({'error': 'username length error'}), 400


    users = db.get_all('User')
    usernames = [user.username for user in users]
    if data['username'] in usernames:
        return jsonify({'error': 'duplicate username'}), 409

    if not validate_inputs(data['email'], 2):
        return jsonify({'error': 'invalid email'}), 400

    emails = [user.email for user in users]
    if data['email'] in emails:
        return jsonify({'error': 'duplicate email'}), 409

    if not validate_inputs(data['password'], 3):
        return jsonify({'error': 'password format error'}), 400

    password = data.pop('password')
    new_user = User(**data)
    new_user.set_password(password)
    new_user.save()

    return jsonify({'registered': True}), 201


@auth.get('/logout', strict_slashes=False)
def logout():
    """logs out a user"""
    logout_user()
    return jsonify({'logout': True})


def validate_inputs(text: str, option: int):
    """
    validates an client inputs
    :param text: the string to validate
    :param option(int): which input to validate
           1: username 2: email 3: password
    """
    username_regex = re.compile(r"^[A-Za-z][A-Za-z0-9]{4,9}$")
    email_regex = re.compile(r"""^[a-z0-9!#$%&'*+/=?^_`{|}~-]+
                            (?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@
                            (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+\.
                            [a-z0-9](?:[a-z0-9-]*[a-z0-9])?$""", re.X)
    passwd_regex = re.compile(r"""^(?=.*[A-Za-z])
                                   (?=.*\d)
                                   [A-Za-z\d\.+-=#_%|&@]{7,}$""", re.X)
    if option == 1 and username_regex.fullmatch(text) is not None:
        return True
    if option == 2 and email_regex.fullmatch(text) is not None:
        return True
    if option == 3 and passwd_regex.fullmatch(text) is not None:
        return True

    return False
