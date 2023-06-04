"""
auth blueprint
"""
from fastapi import APIRouter

auth_router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={401: {"description": "Not authenticated"}}
)

from .views import *
