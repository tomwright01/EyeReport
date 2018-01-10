from flask import Flask, session
from flask_sessionstore import Session

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
session = Session(app)

session.app.session_interface.db.create_all()

from app import views, models