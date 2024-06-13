import os

from flask import Flask
from flask import current_app
from flask import session
from datetime import timedelta

# Extensions
from app.extensions import configurations
from app.extensions import database
from app.extensions import encrypt
from app.extensions import authentication
from app.extensions import command
from app.extensions import localization
from app.extensions import socket
from app.extensions import session

# Blueprints
from app.blueprints import setup
from app.blueprints import webui


def create_app():
    app = Flask(__name__)

    # Extensions
    configurations.init_app(app)
    database.init_app(app)
    encrypt.init_app(app)
    authentication.init_app(app)
    session.init_app(app)
    command.init_app(app)
    localization.init_app(app)
    socket.init_app(app)

    # Bluprints
    setup.init_app(app)
    webui.init_app(app)

    return app
