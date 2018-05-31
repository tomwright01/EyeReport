# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, IntegerField, TextAreaField, SelectField, StringField
from wtforms.validators import InputRequired, Optional

class DataForm(FlaskForm):
    data_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')


class ReportForm(FlaskForm):
    visit_id = IntegerField()
    information = TextAreaField(label='Information',
                                description='Referral information',
                                validators=InputRequired())
    

class ErgReport(ReportForm):
    responses_1 = [('1', 'Within expected limits'),
                   ('2', 'Amplitude mildly reduced'),
                   ('3', 'Amplitude reduced'),
                   ('4', 'Timing delayed'),
                   ('5', 'Not measurable above noise')]
    
    responses_2 = [('1', 'Within expected limits'),
                   ('2', 'b-wave amplitude reduced'),
                   ('3', 'a-wave and b-wave amplitude reduced'),
                   ('4', 'Amplitude reduced, delayed'),
                   ('5', 'Not measurable above noise')]
    
    erg_da001_re = SelectField(label=u'DA 0.01 RE',
                               validators=InputRequired(),
                               choices=responses_1)
    erg_da001_le = SelectField(label=u'DA 0.01 LE',
                               validators=InputRequired(),
                               choices=responses_1)
    erg_da30_re = SelectField(label=u'DA 3.0 RE',
                              validators=InputRequired(),
                              choices=responses_2)
    erg_da30_le = SelectField(label=u'DA 3.0 LE',
                              validators=InputRequired(),
                              choices=responses_2)
    erg_da30op_re = SelectField(label=u'DA OPs RE',
                                validators=InputRequired(),
                                choices=responses_1)
    erg_da30op_le = SelectField(label=u'DA OPs LE',
                                validators=InputRequired(),
                                choices=responses_1)
    erg_la30_re = SelectField(label=u'LA 3.0 RE',
                              validators=InputRequired(),
                              choices=responses_2)
    erg_la30_le = SelectField(label=u'LA 3.0 LE',
                              validators=InputRequired(),
                              choices=responses_2)
    erg_flicker_re = SelectField(label=u'30Hz Flicker RE',
                                 validators=InputRequired(),
                                 choices=responses_1)
    erg_flicker_re = SelectField(label=u'30Hz Flicker RE',
                                 validators=InputRequired(),
                                 choices=responses_1)
    
    erg_da001_re_alt = StringField(label=u'DA 0.01 RE',
                                   validators=Optional())
    erg_da001_le_alt = StringField(label=u'DA 0.01 LE',
                                   validators=Optional())
    erg_da30_re_alt = StringField(label=u'DA 3.0 RE',
                                  validators=Optional())
    erg_da30_le_alt = StringField(label=u'DA 3.0 LE',
                                  validators=Optional())
    erg_da30op_re_alt = StringField(label=u'DA OPs RE',
                                    validators=Optional())
    erg_da30op_le_alt = StringField(label=u'DA OPs LE',
                                    validators=Optional())
    erg_la30_re_alt = StringField(label=u'LA 3.0 RE',
                                    validators=Optional())
    erg_la30_le_alt = StringField(label=u'LA 3.0 LE',
                                    validators=Optional())
    erg_flicker_re_alt = StringField(label=u'30Hz Flicker RE',
                                     validators=Optional())
    erg_flicker_le_alt = StringField(label=u'30Hz Flicker LE',
                                     validators=Optional())
    
    erg_submit = SubmitField('Update ERG')