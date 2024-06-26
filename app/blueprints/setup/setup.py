import os
import csv
import io
import arrow
import requests

# DateTime
from datetime import datetime
from datetime import timedelta

# ICS
import ics

# Slugify
from slugify import slugify

# Flask
from flask import Flask
from flask import redirect
from flask import url_for
from flask import render_template
from flask import request
from flask import flash
from flask import send_file
from flask import make_response
from flask import session
from flask import current_app
from flask import send_from_directory
from flask import jsonify

# QRCode
import qrcode

# Werkzeug
from werkzeug.utils import secure_filename

# Authentication
from app.extensions.authentication import login_manager
from app.extensions.authentication import login_user
from app.extensions.authentication import logout_user
from app.extensions.authentication import login_required
from app.extensions.authentication import current_user

# Encrypt
from app.extensions.encrypt import bcrypt

# Email Validator
from email_validator import validate_email, EmailNotValidError

# SocketIO
from app.extensions.socket import socketio
from app.extensions.socket import emit

# Database Model
from app.extensions.database import db
from app.blueprints.models import Users
from app.blueprints.models import Register
from app.blueprints.models import Event
from app.blueprints.models import Streaming
from app.blueprints.models import Survey
from app.blueprints.models import Message


@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)


def get_event(slug):
    event = Event.query.filter_by(slug=slug.split("/")[1]).one_or_none()
    if event:
        return event


# region Event Functions
@login_required
def events():
    started = Event.query.filter_by(status="started").all()
    next_events = Event.query.filter_by(status="scheduled").all()
    finished_events = Event.query.filter_by(status="finished").all()
    return render_template(
        "events.html",
        next_events=next_events,
        finished_events=finished_events,
        started=started,
    )


@login_required
def add_event():
    if request.method == "POST":
        title = request.form.get("title")
        slug = slugify(title)
        subtitle = request.form.get("subtitle")
        event_date = datetime.strptime(request.form.get("event_date"), "%d.%m.%Y")
        start_time = datetime.strptime(request.form.get("start_time"), "%H:%M")
        end_time = datetime.strptime(request.form.get("end_time"), "%H:%M")
        icalendar = request.form.get("icalendar")
        email = request.form.get("email")
        speakers = request.form.get("speakers")
        status = "scheduled"
    
        event = Event(
            title=title,
            slug=slug,
            subtitle=subtitle,
            date=event_date,
            start=start_time,
            end=end_time,
            icalendar=icalendar,
            email=email,
            speakers=speakers,
            status=status
        )
        flash(
            "[{}] - As configurações foram salvas.".format(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            "alert-success",
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for("setup.events"))
    return render_template("add_event.html")


@login_required
def edit_event(id):
    event = Event.query.filter_by(id=id).one_or_none()
    return render_template("edit_event.html", event=event)


@login_required
def update_event():
    if request.method == "POST":
        id = request.form.get("id")
        
        ''' Check if streaming was configurated '''
        if request.form.get("status") == "started":
            streaming = Streaming.query.filter_by(event_id = id).one_or_none()     
            if streaming is None:
                flash('Antes de iniciar o evento é necessário configurar a transmissão no módulo streaming','alert-danger')
                return redirect(url_for("setup.edit_event", id=id))
        event = Event.query.filter_by(id=id).one_or_none()
        event.status = request.form.get("status")
        event.title = request.form.get("title")
        event.subtitle = request.form.get("subtitle")
        event.slug = slugify(event.title)
        """ UTC-3 to works with momentjs """
        event.date = datetime.strptime(
            request.form.get("date"), "%d/%m/%Y"
        ) + timedelta(hours=3)
        event.start = datetime.strptime(request.form.get("start"), "%H:%M")
        event.end = datetime.strptime(request.form.get("end"), "%H:%M")
        event.icalendar = request.form.get("icalendar")
        event.email = request.form.get("email")
        event.speakers = request.form.get("speakers")
        db.session.commit()
        socketio.emit("event_status", {"slug": event.slug, "status": event.status})
        return redirect(url_for("setup.edit_event", id=id))


@login_required
def calendar(id):
    event = Event.query.filter_by(id=id).one_or_none()

    ics_calendar = ics.Calendar()
    ics_event = ics.Event()

    ics_event.name = event.title
    ics_event.begin = arrow.get(
        datetime.combine(event.date, event.start.time()), current_app.config["TIMEZONE"]
    )
    ics_event.end = arrow.get(
        datetime.combine(event.date, event.end.time()), current_app.config["TIMEZONE"]
    )
    ics_event.created_at = arrow.get(datetime.now(), current_app.config["TIMEZONE"])
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


# endregion Event Functions

# region Survey Functions


@login_required
def survey(event_id):
    event = Event.query.filter_by(id=event_id).one_or_none()
    if event:
        survey = Survey.query.filter_by(event_id=event.id).one_or_none()
        return render_template("survey.html", survey=survey, event=event)


@login_required
def survey_enable():
    if request.method == "POST":
        survey_link = request.form.get("survey_link")
        event_id = request.form.get("event_id")
        survey = Survey.query.filter_by(event_id=event_id).one_or_none()

        if survey is None:
            data = Survey(
                survey_link=survey_link,
                event_id=event_id,
                qrcode=create_qrcode(survey_link),
            )
            db.session.add(data)
            db.session.commit()
            flash(
                "[{}] - Módulo de pesquisa configurado.".format(
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ),
                "alert-success",
            )
        return redirect(url_for("setup.survey", event_id=event_id))


@login_required
def survey_disable():
    if request.method == "POST":
        event_id = request.form.get("event_id")
        survey = Survey.query.filter_by(event_id=event_id).one_or_none()
        if survey is not None:
            if os.path.isfile(
                os.path.join(current_app.config["UPLOAD_FOLDER"], survey.qrcode)
            ):
                os.remove(
                    os.path.join(current_app.config["UPLOAD_FOLDER"], survey.qrcode)
                )
            db.session.delete(survey)
            db.session.commit()
            flash(
                "[{}] - Módulo de pesquisa desativado.".format(
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ),
                "alert-warning",
            )
        return redirect(url_for("setup.survey", event_id=event_id))


@login_required
def create_qrcode(survey_link, qr_image_filename=None):
    if qr_image_filename is not None and os.path.isfile(
        os.path.join(current_app.config["UPLOAD_FOLDER"], qr_image_filename)
    ):
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], qr_image_filename))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(survey_link)
    qr.make(fit=True)

    qr_image_filename = f"qrcode_{generate_timestamp()}.png"
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], qr_image_filename))
    return qr_image_filename


# endregion Survey Functions
@login_required
def streaming(event_id):
    streaming = Streaming.query.filter_by(event_id=event_id).one_or_none()
    event = Event.query.filter_by(id=event_id).one_or_none()
    if request.method == "POST":
        # Save or Update streaming configurations
        source_type = request.form.get("gridHLS")
        if source_type == "liveid":
            liveid = request.form.get("liveid")
            source = f"{current_app.config['CDN_LIVE']}/hls/{liveid}/trr_.m3u8"
        elif source_type == "url":
            source = request.form.get("source")
            if not source:
                flash(
                    "[{}] - Informe a URL da fonte HLS".format(
                        datetime.now().strftime("%d/%m/%Y %H:%M")
                    ),
                    "alert-danger",
                )
                return render_template(
                    "streaming.html", streaming=streaming, event=event
                )
        else:
            flash(
                "[{}] - Informe a Fonte HLS (LiveID ou URL)".format(
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ),
                "alert-danger",
            )
            return render_template("streaming.html", streaming=streaming, event=event)
        if streaming is None:
            data = Streaming(source=source, event_id=event_id, source_type=source_type)
            db.session.add(data)
        else:
            streaming.source = source
            streaming.source_type = source_type
            flash(
                "[{}] - As configurações de Streaming foram salvas.".format(
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ),
                "alert-success",
            )
        db.session.commit()
        poster = request.files["poster"]
        upload_poster(poster, event.id)
        streaming = Streaming.query.filter_by(event_id=event_id).one_or_none()
        return render_template("streaming.html", streaming=streaming, event=event)
    return render_template("streaming.html", streaming=streaming, event=event)


@login_required
def publish_streaming(event_id):
    event = Event.query.filter_by(id=event_id).one_or_none()
    if event.status == "scheduled" or event.status == "finished":
        event.status = "started"
        db.session.commit()
        flash(
            "[{}] - A transmissão do Webinar foi iniciada.".format(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            "alert-success",
        )
    elif event.status == "started":
        event.status = "finished"
        db.session.commit()
        flash(
            "[{}] - A transmissão do Webinar foi encerrada.".format(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            "alert-danger",
        )

    socketio.emit("event_status", {"status": event.status, "slug": event.slug})
    return redirect(url_for("setup.streaming", event_id=event_id))


def upload_poster(poster, event_id):
    if allowed_images(poster.filename):
        if not os.path.isdir(current_app.config["UPLOAD_FOLDER"]):
            os.mkdir(current_app.config["UPLOAD_FOLDER"])
        poster_filename = secure_filename(poster.filename)
        streaming = Streaming.query.filter_by(event_id=event_id).one_or_none()
        if streaming.poster is not None:
            if os.path.isfile(
                os.path.join(current_app.config["UPLOAD_FOLDER"], streaming.poster)
            ):
                os.remove(
                    os.path.join(current_app.config["UPLOAD_FOLDER"], streaming.poster)
                )
        poster.save(os.path.join(current_app.config["UPLOAD_FOLDER"], poster_filename))
        streaming.poster = poster_filename
        db.session.commit()
        return flash(
            "[{}] - Upload do poster realizado com sucesso.".format(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            "alert-success",
        )
    else:
        return (
            "[{}] - Formato da imagem não é suportado, formatos suportados".format(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            "alert-danger",
        )


def allowed_images(image_filename):
    return (
        "." in image_filename
        and image_filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_IMAGES_EXTENSIONS"]
    )


# region SockeIO Functions
online = []


@socketio.on("connect")
def connect(slug=None):
    if slug is not None:
        event = get_event(slug)
        if event is not None and event.status == "started":
            if request.sid not in online:
                online.append({"sid": request.sid, "slug": event.slug})
            emit("users_online", len(online), broadcast=True)


@socketio.on("user_online")
def user_online(message):
    if message["slug"]:
        event = get_event(message["slug"])
        if event is not None and event.status == "started":
            if message["email"] not in online:
                online.append(message["email"])
        emit("users_online", len(online), broadcast=True)


@socketio.on("disconnect")
def disconnect():
    event = Event.query.one_or_none()
    if event is not None and event.status == "started":
        if request.sid in online:
            online.remove(request.sid)
        emit("users_online", len(online), broadcast=True)


@socketio.on("status_streaming")
def status_streaming(message):
    if current_app.config["SUBFOLDER"]:
        if message == "status_enable":
            emit(
                "publish_status",
                "{}/live".format(current_app.config["SUBFOLDER_NAME"]),
                broadcast=True,
            )
        elif message == "status_disable":
            emit(
                "publish_status",
                "{}/schedule".format(current_app.config["SUBFOLDER_NAME"]),
                broadcast=True,
            )
    else:
        if message == "status_enable":
            emit("publish_status", "live", broadcast=True)
        elif message == "status_disable":
            emit("publish_status", "schedule", broadcast=True)


@socketio.on("event_status")
def event_status(message):
    if message == "started":
        emit(
            "event_status",
            "{}/live".format(message["slug"]),
            broadcast=True,
        )
    elif message == "scheduled":
        emit(
            "event_status",
            "{}/schedule".format(message["slug"]),
            broadcast=True,
        )
    elif message == "finished":
        emit(
            "event_status",
            "{}/finished".format(message["slug"]),
            broadcast=True,
        )


# endregion SocketIO Functions

# region Messages Functions
@login_required
def messages(event_id, page=1):
    event = Event.query.filter_by(id = event_id).first()
    messages = Message.query.filter_by(event_id = event_id).order_by(Message.created_at.desc()).paginate(per_page=100, page=page, error_out=True)
    return render_template('messages.html', messages=messages, event=event)

@login_required
def message_delete(event_id, message_id):
    message = Message.query.filter_by(id = message_id).first()
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for("setup.messages", event_id = event_id))


@login_required
def message_export(event_id):
    csv_rows = []
    for message in Message.query.filter_by(event_id=event_id).all():
        register = Register.query.filter_by(id = message.register_id).first()
        if register:
            csv_rows.append(
                {
                    "id": message.id,
                    "created_at": message.created_at,
                    "nickname": message.nickname,
                    "text": message.text,
                    "name": register.name,
                    "email": register.email,
                    "company": register.company
                }
            )
    csv_file = io.StringIO()
    csv_write = csv.DictWriter(
        csv_file,
        fieldnames=[
            "id",
            "created_at",
            "nickname",
            "text",
            "name",
            "email",
            "company"
        ],
        dialect="excel",
    )
    csv_write.writeheader()
    for csv_row in csv_rows:
        csv_row["name"] = str(csv_row["name"]).encode("utf-8").decode("utf-8")
        csv_row["company"] = str(csv_row["company"]).encode("utf-8").decode("utf-8")
        csv_row["text"] = str(csv_row["company"]).encode("utf-8").decode("utf-8")
        csv_write.writerow(csv_row)
    response = make_response(csv_file.getvalue())
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=messages_export_{}.csv".format(datetime.now().strftime("%Y%m%d"))
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    csv_file.close()
    return response

# endregion 
def login():
    users = Users.query.one_or_none()
    if users is not None:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            
            # ReCaptcha
            #recaptcha_site_key = request.form["g-recaptcha-response"]
            #recaptcha_secret = current_app.config["RECAPTCHA_PRIVATE_KEY"]
            #response = requests.post(
            #    f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret}&response={recaptcha_site_key}"
            #).json()
            
            #if not response["success"]:
            #    flash("Erro ao validar o captcha.", "alert-danger")
            #    return redirect(url_for("setup.login"))
            
            user = Users.query.filter_by(email=username).one_or_none()
            if user is not None:
                if (
                    bcrypt.check_password_hash(user.password, password)
                    is True
                ):
                    login_user(user, remember=True)
                    return redirect(url_for("setup.events"))
                else:
                    flash("Usuário e/ou Senha Inválidos.", "alert-danger")
            return render_template("login.html")
        return render_template("login.html")
    else:
        return redirect(url_for("setup.config"))


@login_required
def dashboard(event_id):
    event = Event.query.filter_by(id=event_id).one_or_none()
    
    # Total leads
    registers = (
        Register.query.filter_by(event_id=event_id).order_by(Register.id.desc()).all()
    )
    return render_template("dashboard.html", registers=registers, event=event)

@login_required
def dashboard_count_total_watched(event_id):
    total_watched = Register.query.filter_by(watched = True).filter_by(event_id = event_id).count()
    total_registers = Register.query.filter_by(event_id=event_id).count()
    return render_template('partials/_counter_watched.html', total_watched=total_watched, total_registers = total_registers)


@login_required
def export(event_id):
    csv_rows = []
    for register in Register.query.filter_by(event_id=event_id).all():
        csv_rows.append(
            {
                "id": register.id,
                "date": register.date,
                "name": register.name,
                "phone_number": register.phone_number,
                "email": register.email,
                "cnpj": register.cnpj,
                "company": register.company,
                "watched": register.watched,
                "watched_date": register.watched_date,
            }
        )
    csv_file = io.StringIO()
    csv_write = csv.DictWriter(
        csv_file,
        fieldnames=[
            "id",
            "date",
            "name",
            "phone_number",
            "email",
            "cnpj",
            "company",
            "watched",
            "watched_date",
        ],
        dialect="excel",
    )
    csv_write.writeheader()
    for csv_row in csv_rows:
        csv_row["name"] = str(csv_row["name"]).encode("utf-8").decode("utf-8")
        csv_row["company"] = str(csv_row["company"]).encode("utf-8").decode("utf-8")
        csv_write.writerow(csv_row)
    response = make_response(csv_file.getvalue())
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=export_{}.csv".format(datetime.now().strftime("%Y%m%d"))
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    csv_file.close()
    return response


def logout():
    logout_user()
    return redirect(url_for("setup.login"))


def config():
    users = Users.query.one_or_none()
    if users is not None:
        return redirect(url_for("setup.login"))
    else:
        return render_template("create_admin_user.html")

def create_admin_user():
    if request.method == "POST":
        # Check if user already exists
        users = Users.query.one_or_none()
        if users is not None:
            return redirect(url_for("setup.login"))
        
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
    
        # ReCaptcha
        #recaptcha_site_key = request.form["g-recaptcha-response"]
        #recaptcha_secret = current_app.config["RECAPTCHA_PRIVATE_KEY"]
        #response = requests.post(
        #    f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret}&response={recaptcha_site_key}"
        #).json()
        #fields = {
        #    "fullname": fullname,
        #    "email": email
        #}
        #if not response["success"]:
        #    flash("Erro ao validar o captcha.", "alert-danger")
        #    return redirect(url_for("setup.config"))
    
        # Check password length
        if len(password) < 8:
            flash("A sua senha de acesso deve ter no mínimo 8 caracteres.", "alert-danger")
            return redirect(url_for("setup.config"))
        
        # Check if email address is valid
        
        if not is_valid_email(email):            
            flash("O endereço de e-mail informado não é válido.", "alert-danger")
            return redirect(url_for("setup.config"))
        
        # Create Administrative User
        user = Users(
            fullname=fullname,
            email=email,
            password=bcrypt.generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("setup.login"))

def is_valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        print("Erro")
        return False

# Functions
def generate_timestamp():
    return datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
