from flask import Flask, render_template, redirect, url_for 
from flask_mongoengine import MongoEngine
from flask_talisman import Talisman
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from datetime import datetime
import os

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

from .users.routes import users
from .report.routes import report

def page_not_found(e):
    return render_template("404.html"), 404

def create_app():
    app = Flask(__name__)
    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com',
            'cdn.jsdelivr.net'
        ],
        'img-src': ['\'self\'', 'data:']
    }
    Talisman(app, content_security_policy=csp)
    app.config.from_pyfile("config.py", silent=False)
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(report)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app