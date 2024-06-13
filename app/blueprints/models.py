import uuid
from datetime import datetime
from datetime import timezone
from app.extensions.database import db
from app.extensions.authentication import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        unique=True,
        default=lambda: str(uuid.uuid4().hex),
    )
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Users(BaseModel, UserMixin):
    email = db.Column(db.String(255), nullable=False, unique=True)
    fullname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, email, password, fullname=None):
        self.email = email
        self.fullname = fullname
        self.password = password

class Event(BaseModel):
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    subtitle = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    icalendar = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    speakers = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    
    # One-to-Many
    registers = db.relationship('Register', backref='event', lazy=True)
    messages = db.relationship('Message', backref='event', lazy=True)
    
    # One-to-One
    streaming = db.relationship('Streaming', backref='event', lazy="select", uselist=False)
    survey = db.relationship('Survey', backref='event', lazy="select", uselist=False)

    def __init__(
        self,
        title,
        slug,
        subtitle,
        icalendar,
        email,
        speakers,
        date,
        start,
        end,
        status,
    ):
        self.title = title
        self.slug = slug
        self.subtitle = subtitle
        self.date = date
        self.start = start
        self.end = end
        self.icalendar = icalendar
        self.email = email
        self.speakers = speakers
        self.status = status


class Streaming(BaseModel):
    source = db.Column(db.String(255), nullable=True)
    source_type = db.Column(db.String(50), nullable=True)
    poster = db.Column(db.String(100), nullable=True, default="")
    
    # ForeignKeys
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)

    def __init__(self, source, source_type, event_id, poster=None):
        self.source = source
        self.poster = poster
        self.event_id = event_id
        self.source_type = source_type


class Register(BaseModel):
    date = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    action = db.Column(db.Integer, nullable=True)
    watched = db.Column(db.Integer, nullable=True)
    watched_date = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    messages = db.relationship('Message', backref=db.backref('events', lazy=True))
    
    # ForeignKeys
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)

    def __init__(
        self,
        name,
        event_id,
        phone_number,
        email,
        date=datetime.now(),
        action=False,
        watched=False,
        watched_date=None,
    ):
        self.name = name
        self.event_id = event_id
        self.date = date
        self.phone_number = phone_number
        self.email = email
        self.action = action
        self.watched = watched
        self.watched_date = watched_date


class Survey(BaseModel):
    survey_link = db.Column("survey_link", db.String(255), nullable=True)
    qrcode = db.Column("qrcode", db.String(255), nullable=True)
    
    # ForeignKeys
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)
    
    def __init__(self, survey_link, event_id, qrcode):
        self.survey_link = survey_link
        self.event_id = event_id
        self.qrcode = qrcode


class Message(BaseModel):
    nickname = db.Column("nickname", db.String(50), nullable=False)
    text = db.Column("text", db.Text, nullable=False)
    
    # ForeignKeys
    event_id = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)
    register_id = db.Column(db.String(36), db.ForeignKey('register.id'), nullable=False)

    def __init__(self, nickname, event_id, register_id, text):
        self.nickname = nickname
        self.event_id = event_id
        self.register_id = register_id
        self.text = text