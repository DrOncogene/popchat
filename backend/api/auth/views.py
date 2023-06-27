#!usr/bin/env python3
"""
authentication endpoints
"""
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Annotated
from fastapi import Cookie, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from mongoengine.errors import NotUniqueError

from models.user import User
from storage import db, cache
from api.models import UserIn, UserBase
from . import auth_router


@auth_router.post('/register', status_code=201)
async def register(user: UserIn) -> JSONResponse:
    """login route"""
    username = user.username
    email = user.email
    passwd = user.password

    if db.get_by_username(username):
        raise HTTPException(status_code=409,
                            detail="username already exists")
    if db.get_by_email(email):
        raise HTTPException(status_code=409, detail="email already exists")
    new_user = User(username=username, email=email)
    new_user.set_password(passwd)
    try:
        new_user.save()
    except NotUniqueError as err:
        raise HTTPException(status_code=409,
                            detail="username or email already exists")
    except Exception as err:
        raise HTTPException(status_code=500, detail='Error creating user')

    return JSONResponse({"message": "Registration success"}, 201)


@auth_router.post('/login')
async def login(
    user: UserIn,
    response: JSONResponse,
    JWT: Annotated[AuthJWT, Depends()]
) -> UserBase:
    login_id = user.username or user.email
    if not login_id:
        raise HTTPException(status_code=400,
                            detail="username or email required")

    if user.username:
        the_user = db.get_by_username(login_id)
    else:
        the_user = db.get_by_email(login_id)

    if not the_user:
        raise HTTPException(status_code=404, detail='User does not exist')

    if not the_user.validate_password(user.password):
        raise HTTPException(status_code=401, detail='Invalid password')

    new_token = JWT.create_access_token(the_user.username)
    cache.set(new_token, str(the_user.id))
    the_user.save()

    response.set_cookie(
        '_popchat_auth',
        new_token,
        httponly=True,
        samesite='strict',
        expires=datetime.now(timezone.utc) + timedelta(days=1)
    )

    return UserBase(**the_user.to_dict())


@auth_router.get('/is_authenticated')
def is_authenticated(
    token: Annotated[str, Cookie(alias='_popchat_auth')],
    JWT: Annotated[AuthJWT, Depends()]
) -> UserBase:
    try:
        JWT.jwt_required()
    except Exception as err:
        raise HTTPException(status_code=401, detail='Invalid token')

    user_id = cache.get(token)
    user = db.get_by_id(User, str(user_id, encoding='utf-8'))
    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')

    return user.to_dict()


@auth_router.get('/logout')
async def logout(
    token: Annotated[str, Cookie(alias='_popchat_auth')]
) -> JSONResponse:
    user_id = cache.get(token)
    user = db.get_by_id(User, str(user_id, encoding='utf-8'))
    if not user:
        return HTTPException(status_code=401, detail='Invalid token')

    return JSONResponse({'detail': 'success'})

@auth_router.get('/forgot_password')
async def get_reset_token(email: str, response: JSONResponse) -> JSONResponse:
    user = db.get_by_email(email)
    if not user:
        return HTTPException(status_code=404, detail='User does not exist')

    reset_token = token_hex()
    user.reset_token = reset_token
    user.save()
    response.headers['X-Reset-Token'] = reset_token

    # FIXME: Add logic to send email to user with a link pointing to form
    # where they can change password.
    # format of link:
    #        https://<domain>/reset_password/{reset_token}
    #       HTTP method = GET

    return JSONResponse({'detail': 'success'})

@auth_router.get('/reset_password/{reset_token}')
async def get_reset_pass_form(reset_token: str):
    """"""
    user = db.get_by_reset_token(reset_token)
    if not user:
        return HTTPException(status_code=404, detail='No user found')

    # TODO: Add logic to send password reset form to user
    pass

# TODO: Once user confirms through email and a reset token is created,
# the token is used to access this endpoint that will reset the password
@auth_router.post('/reset_password/{reset_token}}')
async def reset_password(
    reset_token: str,
    new_password: Annotated[str, Form()]
):
    user = db.get_by_reset_token(reset_token)
    if not user:
        return HTTPException(status_code=404, detail='No user found')

    user.set_password(new_password)
    user.save()

    return JSONResponse({'detail': 'New password created successfully'})
