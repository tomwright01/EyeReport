import logging, re
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
    app.register_blueprint(reports_bp, url_prefix='/reports')

    app.logger.setLevel(logging.DEBUG)
    return app

from app import models

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval
#
#texenv = app.create_jinja_environment()
#texenv.block_start_string = '((*'
#texenv.block_end_string = '*))'
#texenv.variable_start_string = '((('
#texenv.variable_end_string = ')))'
#texenv.comment_start_string = '((='
#texenv.comment_end_string = '=))'
#texenv.filters['escape_tex'] = escape_tex