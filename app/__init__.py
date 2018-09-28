import logging
from flask import Flask, request, current_app
from flask_sessionstore import Session


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from config import Config

db = SQLAlchemy()
migrate = Migrate()
sess = Session()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app)
    sess.init_app(app)
    
    app.session_interface.db.create_all()
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    from app.imports import bp as imports_bp
    app.register_blueprint(imports_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    app.logger.setLevel(logging.DEBUG)
    return app

from app import models