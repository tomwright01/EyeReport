# -*- coding: utf-8 -*-
from flask import Blueprint

bp = Blueprint('reports', __name__,
               template_folder='templates',
               static_folder='static')

from app.reports import routes
