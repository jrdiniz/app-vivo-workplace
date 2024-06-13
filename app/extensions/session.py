from flask_session import Session

def init_app(app):
    session = Session()
    session.init_app(app)
