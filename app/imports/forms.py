# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField

class DataForm(FlaskForm):
    data_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')