import os
import time
import base64
import hashlib
import json
import requests
import arrow
import ics
import io
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import session
from flask import make_response
from flask import send_from_directory
from flask import jsonify
from flask import current_app
from flask import flash

# SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import or_

# Extensions
from app.extensions.database import db
from app.extensions.csrf import csrf

from app.extensions.socket import socketio
from app.extensions.socket import emit
from app.extensions.socket import send
from app.extensions.socket import join_room

# Model
from app.blueprints.models import Register
from app.blueprints.models import Event
from app.blueprints.models import Streaming
from app.blueprints.models import Survey
from app.blueprints.models import Message

# Functools
from functools import wraps

# Decorators
def event_status(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        event = get_event()
        if event is not None:
            cookie = request.cookies.get(event.slug)
            webinar_routes_rules = request.url_rule
            if cookie != None:
                if (
                    event.status == "scheduled"
                    and "/<string:slug>/schedule" not in webinar_routes_rules.rule
                ):
                    return redirect(url_for("webui.schedule", slug=event.slug))
                elif (
                    event.status == "finished"
                    and "/<string:slug>/finished" not in webinar_routes_rules.rule
                ):
                    return redirect(url_for("webui.finished", slug=event.slug))
                elif (
                    event.status == "started"
                    and "/<string:slug>/live" not in webinar_routes_rules.rule
                ):
                    return redirect(url_for("webui.live", slug=event.slug))
            elif "/<string:slug>" not in webinar_routes_rules.rule:
                return redirect(url_for("webui.landing", slug=event.slug))
        elif event is None:
            return redirect(url_for("setup.login"))
        return f(*args, **kwargs)

    return decorated_function


def get_event():
    slug = request.url.split("/")
    event = Event.query.filter_by(slug=slug[3]).one_or_none()
    return event


def index():
    events = Event.query.order_by(desc("date")).limit(10).all()
    event_schedule = Event.query.filter(or_(Event.status=="scheduled", Event.status =="started")).order_by(desc("date")).first()
    if event_schedule:
        return redirect(url_for("webui.landing", slug=event_schedule.slug))
    elif events:
        return render_template("index.html", events=events)
    else:
        return redirect(url_for("setup.login"))


@event_status
def landing(slug):
    event = get_event()
    event_date_utc = event.date.astimezone(timezone.utc)
    if event:
        return render_template("landing.html", event=event, event_date_utc=event_date_utc)
    return redirect(url_for("webui.index"))


@event_status
def schedule(slug):
    event = get_event()
    event_date_utc = event.date.astimezone(timezone.utc)
    if event:
        return render_template("schedule.html", event=event, event_date_utc=event_date_utc)
    return redirect(url_for("webui.index"))


@event_status
def finished(slug):
    event = get_event()
    if event:
        return render_template("finished.html", event=event)
    return redirect(url_for("webui.index"))


@event_status
def live(slug):
    event = get_event()
    streaming = Streaming.query.filter_by(event_id=event.id).one_or_none()
    survey = Survey.query.filter_by(event_id=event.id).one_or_none()
    messages = Message.query.filter_by(event_id = event.id).all()
    register_id = request.cookies.get("register")
    if register_id:
        register = Register.query.filter_by(id = register_id).first()
        if register.watched == False:
            register.watched = True
            register.watched_date = datetime.now()
        db.session.commit()
        nickname = register.email.split("@")[0]
        return render_template(
            "live.html", streaming=streaming, survey=survey, event=event, messages=messages, nickname = nickname, register = register
        )
    else:
        return redirect(url_for('webui.flush', slug = event.slug))

def event_register(slug):
    if request.method == "POST":
        event = get_event()
        name = request.form.get("name")
        phone_number = 00000000000
        email = request.form.get("email")
        register = Register.query.filter_by(event_id=event.id, email=email).one_or_none()
        recaptcha_site_key = request.form["g-recaptcha-response"]
        recaptcha_secret = current_app.config["RECAPTCHA_PRIVATE_KEY"]
        response = requests.post(
            f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret}&response={recaptcha_site_key}"
        ).json()
        fields = {
            "name": name,
            "phone_number": phone_number,
            "email": email
        }
        if response.get("success"):
            if register is None:
                register = Register(
                    name=name,
                    phone_number=phone_number,
                    email=email,
                    date=datetime.now(),
                    event_id=event.id,
                )
                db.session.add(register)
                db.session.commit()
            response = make_response(redirect(url_for("webui.live", slug=event.slug)))
            response.set_cookie(
                key=slug,
                value=email,
                max_age=60 * 60 * 24 * 10,
            )
            response.set_cookie(
                key="register",
                value=register.id,
                max_age=60 * 60 * 24 * 10,
            )
            return response
        else:
            flash("Favor responder o desafio reCAPTCHA.", "alert-danger")
            return render_template("landing.html", event=event, fields=fields)
    return redirect(url_for("webui.index"))


def flush(slug):
    response = make_response(redirect(url_for("webui.landing", slug=slug)))
    response.set_cookie(slug, "", max_age=0)
    response.set_cookie("register", "",max_age=0)
    return response


def calendar(slug):
    event = Event.query.filter_by(slug=slug).one_or_none()

    ics_calendar = ics.Calendar()
    ics_event = ics.Event()

    ics_event.name = event.title
    ics_event.begin = arrow.get(
        datetime.combine(event.date, event.start.time()), current_app.config["TIMEZONE"]
    )
    ics_event.end = arrow.get(
        datetime.combine(event.date, event.end.time()), current_app.config["TIMEZONE"]
    )
    ics_event.created = arrow.get(datetime.now(), current_app.config["TIMEZONE"])
    ics_event.description = render_template("calendar.html", event=event)
    ics_event.organizer = event.email
    ics_event.location = request.url_root
    ics_event.url = request.url_root
    ics_calendar.events.add(ics_event)
    ics_file = io.StringIO()
    ics_file.writelines(ics_calendar)
    response = make_response(ics_file.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename={}.ics".format(
        event.slug
    )
    response.headers["Content-type"] = "text/calendar; charset=utf-8"
    return response


# Socket Routes
connected_clients = 0

@socketio.on("connect")
def on_connect():
    global connected_clients
    connected_clients += 1
    print(f"Connected Clients: {connected_clients}")
    emit("server online users", {"data": "connected"})

@socketio.on("disconnect")
def on_disconnect():
    global connected_clients
    connected_clients -= 1
    print(f"Connected Clients: {connected_clients}")
    print("Client disconnected...")


@socketio.on("message from user")
def receive_message(message):
    message = Message(nickname=message["nickname"], text=message["text"], event_id=message["event_id"], register_id = message["register_id"])
    db.session.add(message)
    db.session.commit()
    emit(
        "message from server",
        {
            "nickname": message.nickname,
            "text": message.text,
            "create_at": message.created_at.strftime("%d/%m/%Y %H:%M"),
            "message_id": message.id,
            "register_id": message.register_id
        },
        broadcast=True,
    )


@socketio.on("send delete chat message")
def delete_message(message_id):
    message = Message.query.filter_by(id=message_id).first()
    if message:
        response = {"message_id": message_id, "nickname": message.nickname, "register_id": message.register_id}
        db.session.delete(message)
        db.session.commit()
        emit("receive delete chat message", response, broadcast=True)


def static_content():
    return send_from_directory("static", request.path[1:])
