import click
from flask_migrate import Migrate
from app.extensions.database import db
from app.extensions.encrypt import bcrypt
from app.blueprints.models import Users

migrate = Migrate()


def init_app(app):
    migrate.init_app(app, db)

    # CLI
    @app.cli.command("create-user")
    @click.argument("email")
    def create_user(email):
        profile = Users.query.filter_by(email=email).one_or_none()
        if profile is None:
            user = Users(
                fullname='Engenharia de Video', email=email, password=bcrypt.generate_password_hash("dROjpPxmp2aXh7")
            )
            db.session.add(user)
            db.session.commit()
            print("User {} was created.".format(email))
