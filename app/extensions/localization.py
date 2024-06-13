from flask_moment import Moment
moment = Moment()

def init_app(app):
    moment.init_app(app)
