"""
defines the api v1 blueprint
"""
from flask import Blueprint

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

from .views import *
