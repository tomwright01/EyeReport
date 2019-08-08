# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from app.models import get_doctors, get_diagnosis
from wtforms.fields import StringField, SelectField, FormField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import InputRequired, Optional, Email, Regexp

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
                        validators = [InputRequired()])
    lname = StringField('Last name',
                        validators = [InputRequired()])
    gender = SelectField('Gender',
                         choices = [('male', 'male'),
                                    ('female','female')])
    dob = DateField('Date of birth', format='%Y-%m-%d',
                    validators = [InputRequired()])
    submit = SubmitField('Add Patient')
    

class DoctorForm(FlaskForm):
    fname = StringField('First name',
                        validators = [InputRequired()])
    lname = StringField('Last name',
                        validators = [InputRequired()])
    phone = StringField('Phone #',
                        validators = [Optional(), Regexp("\d{3}[ ,-]?\d{3}[ ,-]?\d{4}", message="Phone number format NNN-NNN-NNNN")])
    fax = StringField('Fax #',
                      validators = [Optional(), Regexp("\d{3}[ ,-]?\d{3}[ ,-]?\d{4}", message="Phone number format NNN-NNN-NNNN")])
    email = StringField('Email',
                        validators=[Optional(), Email()])
    prefered_contact = SelectField('Prefered contact method',
                                   choices = [('fax','fax'),
                                              ('email', 'email'),
                                              ('both', 'both')],
                                   validators = [InputRequired()])
    
    submit = SubmitField('Add Doctor')
    
class DiagnosisForm(FlaskForm):
    name = StringField('Name',
                       validators = [InputRequired()])
    submit = SubmitField('Add Diagnosis')
    
class VisitForm(FlaskForm):
    dov = DateField('Date of visit', format='%Y-%m-%d',
                    validators = [InputRequired()])
    notes = TextAreaField(label=u'Notes',
                          description='Visit notes (not included on report)',
                          validators=[Optional()])