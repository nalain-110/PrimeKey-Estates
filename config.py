import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "primekey-estates-secret-2024-xK9#mP$2")

    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url or ("sqlite:///" + os.path.join(BASE_DIR, "primekey.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "images", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    WTF_CSRF_ENABLED = True
