#!usr/bin/env python3
"""
authentication endpoints
"""
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Annotated
from fastapi import Cookie, Form, Depends, Header, Response
from fastapi_jwt_auth import AuthJWT
from mongoengine.errors import NotUniqueError

from models.user import User
from storage import db
from api.models import UserIn, UserOut
from . import auth_router


@auth_router.post('/register', status_code=201)
async def register(user: UserIn) -> Response:
    """login route"""
    username = user.username
    email = user.email
    passwd = user.password

    if not username or not email or not passwd:
        return Response(status_code=400,
                        content="username, email and password required")
    new_user = User(username=username, email=email)
    new_user.set_password(passwd)
    try:
        new_user.save()
    except NotUniqueError as err:
        return Response( content=str(err), status_code=409)
    except Exception as err:
        return Response(content=str(err), status_code=500)

    return Response("success")
    


@auth_router.post('/login')
async def login(
    user: UserIn,
    response: Response,
    JWT: Annotated[AuthJWT, Depends()]
) -> UserOut:
    login_id = user.username or user.email
    if not login_id:
        return Response(status_code=400, content="username or email required")

    if user.username:
        the_user = db.get_by_username(login_id)
    else:
        the_user = db.get_by_email(login_id)

    if not the_user:
        return Response('User does not exist', status_code=404)

    if not the_user.validate_password(user.password):
        return Response('Invalid password', status_code=401)

    new_token = str(JWT.create_access_token(identity=the_user.username))
    the_user.auth_token = new_token
    the_user.save()

    response.set_cookie(
        'auth',
        new_token,
        httponly=True,
        samesite='strict',
        expires=datetime.now(timezone.utc) + timedelta(days=1)
    )
    return UserOut(**the_user.to_dict())


@auth_router.get('/logout')
async def logout(token: Annotated[str, Cookie(alias='auth')]) -> Response:
    user = db.get_by_token(token)
    if not user:
        return Response('Invalid token', status_code=401)

    user.auth_token = None
    user.save()

    return Response('success')


@auth_router.get('/forgot_password')
async def get_reset_token(email: str, response: Response) -> Response:
    user = db.get_by_email(email)
    if not user:
        return Response('User does not exist', status_code=404)

    reset_token = token_hex()
    user.reset_token = reset_token
    user.save()
    response.headers['X-Reset-Token'] = reset_token

    return Response('success')


@auth_router.post('/reset_password/{reset_token}}')
async def reset_password(reset_token: str, new_password: Annotated[str, Form()]):
    pass
