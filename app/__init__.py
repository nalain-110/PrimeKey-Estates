from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.blueprints.public.routes import public_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.client.routes import client_bp
    from app.blueprints.agent.routes import agent_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(agent_bp, url_prefix='/agent')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create all tables
    with app.app_context():
        db.create_all()

    return app
