import time
import requests
import base64
import hashlib
import json
from datetime import datetime
from flask_apscheduler import APScheduler
from app.extensions.database import db
from app.extensions.socket import socketio

# Models
from app.blueprints.models import Comment
from app.blueprints.models import Register

scheduler = APScheduler()


def init_app(app):
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.task(
        "interval", id="task_get_users_online", seconds=15, misfire_grace_time=900
    )
    def get_users_online():
        with app.app_context():
            comment = Comment.query.one_or_none()
            if comment:
                timestamp = str(int(time.time()))
                muut_hash = "{}:{}".format(comment.muut_key, timestamp)
                signature = hashlib.sha256(
                    comment.muut_secret_key.encode("utf-8")
                ).update(muut_hash.encode("utf-8"))
                response = requests.get(
                    "https://rest-api.muut.com/v1/forum/{}/online".format(
                        comment.muut_community
                    ),
                    headers={
                        "x-muut-timestamp": timestamp,
                        "x-muut-key": comment.muut_key,
                        "x-muut-signature": signature,
                    },
                )
                users = response.json()["users"]
                socketio.emit("users_connected", len(users))
                for user in users:
                    registers = Register.query.filter(
                        Register.email.like("%{}%".format(user["displayname"]))
                    ).all()
                    for register in registers:
                        if bool(register.watched) is not True:
                            register.watched = True
                            db.session.commit()
