# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from app.models import Patient, get_doctors, get_diagnosis
from wtforms.fields import StringField, SelectField, IntegerField, FormField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp

class PatientForm(FlaskForm):
    doctor = QuerySelectField('Doctors',
                              query_factory=get_doctors,
                              get_label='formatted_name',
                              allow_blank=True)
    
    diagnosis = QuerySelectMultipleField('Diagnoses',
                                         query_factory=get_diagnosis,
                                         get_label='name',
                                         allow_blank=True)

class PatientPhiForm(PatientForm):
    fname = StringField('First name',
                        validators = [DataRequired()])
    lname = StringField('Last name',
                        validators = [DataRequired()])
    sex = SelectField('Gender',
                      choices = [('male', 'male'),
                                 ('female','female')])
    dob = DateField('Date of birth', format='%Y/%m/%d')
    

class DoctorForm(FlaskForm):
    fname = StringField('First name',
                        validators = [DataRequired()])
    lname = StringField('Last name',
                        validators = [DataRequired()])
    phone = StringField('Phone #',
                        validators = [Optional(), Regexp("\d{3}[ ,-]?\d{3}[ ,-]?\d{4}", message="Phone number format NNN-NNN-NNNN")])
    fax = StringField('Fax #',
                      validators = [Optional(), Regexp("\d{3}[ ,-]?\d{3}[ ,-]?\d{4}", message="Phone number format NNN-NNN-NNNN")])
    email = StringField('Email',
                        validators=[Optional(), Email()])
    submit = SubmitField('Add Doctor')
    
class DiagnosisForm(FlaskForm):
    name = StringField('Name',
                       validators = [DataRequired()])
    submit = SubmitField('Add Diagnosis')
    