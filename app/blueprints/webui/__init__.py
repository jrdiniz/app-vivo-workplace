from flask import Blueprint
from flask import current_app
from .webui import index
from .webui import landing
from .webui import live
from .webui import event_register
from .webui import flush
from .webui import schedule
from .webui import static_content
from .webui import calendar
from .webui import finished

bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static")

# Next Events
index.methods = ["GET"]
bp.add_url_rule("/", view_func=index)
bp.add_url_rule("/index", view_func=index)

# Landing
landing.methods = ["GET"]
bp.add_url_rule("/<string:slug>", view_func=landing)

# Register
event_register.methods = ["POST", "GET"]
bp.add_url_rule("/<string:slug>/register", view_func=event_register)

# Live
bp.add_url_rule("/<string:slug>/live", view_func=live)

# Schedule
bp.add_url_rule("/<string:slug>/schedule", view_func=schedule)

# Finish
bp.add_url_rule("/<string:slug>/finished", view_func=finished)

# Flush Session
bp.add_url_rule("/<string:slug>/flush", view_func=flush)

# Static
bp.add_url_rule("/robots.txt", view_func=static_content)
bp.add_url_rule("/sitemap.xml", view_func=static_content)

# Generate ICS File (Calendar)
bp.add_url_rule("/<string:slug>/calendar", view_func=calendar)


def init_app(app):
    with app.app_context():
        app.register_blueprint(bp, url_prefix="/")
