from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import send
from flask_socketio import join_room

socketio = SocketIO()


def init_app(app):
    socketio.init_app(app, logger=True, engineio_logger=True, cors_allowed_origins="*")
