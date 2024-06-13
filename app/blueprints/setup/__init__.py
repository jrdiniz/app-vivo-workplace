from flask import Blueprint
from flask import current_app
from .setup import login
from .setup import logout
from .setup import streaming
from .setup import calendar
from .setup import publish_streaming

# Dashboard Functions
from .setup import dashboard
from .setup import dashboard_count_total_watched
from .setup import export

# Survey Functions
from .setup import survey
from .setup import survey_enable
from .setup import survey_disable

# Event Functions
from .setup import events
from .setup import add_event
from .setup import edit_event
from .setup import update_event

# Messages Functions
from .setup import messages
from .setup import message_delete
from .setup import message_export

# Config Application
from .setup import config
from .setup import create_admin_user

bp = Blueprint("setup", __name__, template_folder="templates", url_prefix="/setup", static_folder="static")


# region Events
events.methods = ["GET"]
bp.add_url_rule("/", view_func=events)

# Add Event
add_event.methods = ["GET", "POST"]
bp.add_url_rule("/event/add", view_func=add_event)

# Edit Event
edit_event.methods = ["GET", "POST"]
bp.add_url_rule("/event/edit/<id>", view_func=edit_event)

# Update Event
update_event.methods = ["POST"]
bp.add_url_rule("/event/update", view_func=update_event)
# endregion Events

# Dashboard
bp.add_url_rule("/dashboard/<event_id>", view_func=dashboard)
bp.add_url_rule("/export/<event_id>", view_func=export)

dashboard_count_total_watched.methods = ["GET"]
bp.add_url_rule("/dashboard/count_watched/<event_id>", view_func=dashboard_count_total_watched)

# Streaming
streaming.methods = ["POST", "GET"]
bp.add_url_rule("/streaming/<event_id>", view_func=streaming)

# Publish Streaming
publish_streaming.methods = ["GET"]
bp.add_url_rule("/publish/<event_id>", view_func=publish_streaming)

# Login
login.methods = ["GET", "POST"]
bp.add_url_rule("/login", view_func=login)

# Logout
logout.methods = ["GET"]
bp.add_url_rule("/logout", view_func=logout)

# Config
create_admin_user.methods = ["POST"]
bp.add_url_rule("/user/add", view_func=create_admin_user)

config.methods = ["GET"]
bp.add_url_rule("/config", view_func=config)

# Download ICS File (Calendar)
bp.add_url_rule("/calendar/<id>", view_func=calendar)

# Survey Routes
survey.methods = ["POST", "GET"]
bp.add_url_rule("/survey/<event_id>", view_func=survey)

survey_enable.methods = ["POST"]
bp.add_url_rule("/survey/enable", view_func=survey_enable)

survey_disable.methods = ["POST"]
bp.add_url_rule("/survey/disable", view_func=survey_disable)

# Messages Routes
messages.methods = ["GET"]
bp.add_url_rule("/messages/<event_id>", view_func=messages)
bp.add_url_rule("/messages/<event_id>/<int:page>", view_func=messages)

message_delete.methods = ["GET"]
bp.add_url_rule("/message/delete/<event_id>/<message_id>", view_func=message_delete)

message_export.methods = ["GET"]
bp.add_url_rule("/message/delete/<event_id>", view_func=message_export)

def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/setup")
