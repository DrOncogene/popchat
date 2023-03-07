"""
init file - defines the factory function
"""
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager
from flask_session import Session

from storage import db
from app.auth import auth
from app.api.v1 import api_v1

cors = CORS()
sio = SocketIO()
login_manager = LoginManager()
# session_manager = Session()


def create_app(config):
    """the app factory"""
    app = Flask(__name__)

    # load config files
    app.config.from_object(config)

    # init extensions
    cors.init_app(app, resources={r"/auth/*": {"origins": "*"}})
    sio.init_app(app, cors_allowed_origins=r'*', async_mode='eventlet')
    login_manager.init_app(app)
    # session_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def get_user(user_id):
        """
        loads the user from db
        """
        return db.get_one('User', user_id)

    @app.teardown_appcontext
    def close_session(err):
        db.close()

    with app.app_context():
        app.register_blueprint(auth)
        app.register_blueprint(api_v1)

    return app
