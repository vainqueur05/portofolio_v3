import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pour les uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo max
    UPLOAD_FOLDER = 'app/static/images/uploads'
    # Autres configurations
    COMPRESS_ENABLED = True
    CACHE_TYPE = 'simple'
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    GA_TRACKING_ID = os.getenv('GA_TRACKING_ID', '')
    LOG_DIR = 'logs'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_MAX_BYTES = 1024 * 1024 * 10  # 10 Mo
    LOG_BACKUP_COUNT = 5
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 an

def setup_logging(app):
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT'],
        encoding='utf-8'  # ← Ajoutez ce paramètre
    )
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application démarrée')