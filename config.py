import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Default
    SECRET_KEY = os.getenv('SECRET_KEY')
    TIMEZONE = "America/Sao_Paulo"


class ProductionConfig(Config):
    # Debug
    DEBUG = False
    
    # MySQL Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}"
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Images
    IMAGES_FOLDER = BASE_DIR + "/app/static/images"
    UPLOAD_FOLDER = BASE_DIR + "/app/static/uploads"
    ALLOWED_IMAGES_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(minutes=120)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False

    # Google reCAPTCHA v2
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = "6LflkcsZAAAAADX-eNQkBOdI6P_fWdIQ9nlrhaJe"
    RECAPTCHA_PRIVATE_KEY = "6LflkcsZAAAAAFj1UJXn4bx4ihrNzX5mc0ArfJkC"
    RECAPTCHA_OPTIONS = {"theme": "white"}
    
    # Server Side Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "session_"
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=120)
    SESSION_FILE_DIR = f"{BASE_DIR}/session"
    
    # CDN
    CDN_LIVE = "https://live-corp-cf.terra.com.br"
    CDN_VOD = "https://pd-corp-cf.terra.com.br"


class DevelopmentConfig(Config):
    # Debug
    DEBUG = True

    # MySQL Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}"
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    IMAGES_FOLDER = BASE_DIR + "/app/static/images"
    UPLOAD_FOLDER = BASE_DIR + "/app/static/uploads"
    ALLOWED_IMAGES_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(minutes=120)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False

    # Google reCAPTCHA v2
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = "6LflkcsZAAAAADX-eNQkBOdI6P_fWdIQ9nlrhaJe"
    RECAPTCHA_PRIVATE_KEY = "6LflkcsZAAAAAFj1UJXn4bx4ihrNzX5mc0ArfJkC"
    RECAPTCHA_OPTIONS = {"theme": "white"}
    
    # Server Side Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "session_"
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=120)
    SESSION_FILE_DIR = f"{BASE_DIR}/session"

    # CDN
    CDN_LIVE = "https://live-corp-cf.terra.com.br"
    CDN_VOD = "https://pd-corp-cf.terra.com.br"