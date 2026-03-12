# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_compress import Compress
from flask_caching import Cache
from config import Config
from flask import render_template
from config import setup_logging

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
compress = Compress()
cache = Cache()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    setup_logging(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    compress.init_app(app)
    cache.init_app(app)

    # ⬇️ AJOUTEZ CE BLOC ICI ⬇️
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    # ⬆️ FIN DU BLOC À AJOUTER ⬆️

    # Enregistrement des blueprints (inchangé)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # si vous utilisez une base de données
        return render_template('errors/500.html'), 500

    return app