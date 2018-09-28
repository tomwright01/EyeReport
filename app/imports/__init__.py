# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('imports', __name__,
               template_folder='templates')

from app.imports import routes