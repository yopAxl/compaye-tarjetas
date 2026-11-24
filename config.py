import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'compaye-tarjetas-dev-key-2026')

    # --- Database ---
    DATABASE_DIR = os.path.join(basedir, 'database')
    DATABASE_PATH = os.path.join(DATABASE_DIR, 'compaye.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- File Uploads ---
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'tarjetas')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max per file
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # --- Thumbnail ---
    THUMBNAIL_SIZE = (400, 400)
