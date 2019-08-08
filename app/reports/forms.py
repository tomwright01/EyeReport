# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, TextAreaField, SelectField, StringField, BooleanField, DecimalField
from wtforms.validators import InputRequired, Optional, Length
from decimal import ROUND_HALF_UP

def required_field(testType=None, message=None):
    """ Validator,
    input required if test has been performed.
    Test must be one of (None, 'ERG', MFERG', 'VEP')
    """
    if not message:
        message = "My Input required"
    
    if not testType:
        return InputRequired(message)
    
    testType = testType.upper()
    
    switcher = {'ERG': 'form.ergComplete',
                'MFERG': 'form.mfergComplete',
                'VEP': 'form.vepComplete',
                'EOG': 'form.eogComplete'}
    
    _checkField = switcher.get(testType)
    
    def _required_field(form, field):
        if eval(_checkField).data:
            InputRequired(message)(form, field)
        else:
            Optional(message)(form, field)
    
    return _required_field

class ReportForm(FlaskForm):
    visit_id = IntegerField()
    information = TextAreaField(label=u'Information',
                                description='Referral information',
                                validators=[InputRequired()])
    ergComplete = BooleanField(label=u'ERG Complete',
                               description='ERG performed',
                               default=True)
    mfergComplete = BooleanField(label=u'mfERG Complete',
                                 description='mfERG performed',
                                 default=True)
    vepComplete = BooleanField(label=u'VEP Complete',
                               description='VEP performed',
                               default=True)
    eogComplete = BooleanField(label=u'EOG Complete',
                               description='EOG performed',
                               default=True)
    testComment = TextAreaField(label=u'Summary',
                                description='Test summary',
                                validators=[InputRequired()])
class ErgReport(ReportForm):
    
    erg_da001_re = StringField(label=u'DA 0.01 RE',
                               validators=[required_field('ERG'), Length(2, 80)])
    
    erg_da001_le = StringField(label=u'DA 0.01 LE',
                               validators=[required_field('ERG'), Length(2, 80)])
    erg_da3_re = StringField(label=u'DA 3.0 RE',
                              validators=[required_field('ERG'), Length(2, 80)])
    erg_da3_le = StringField(label=u'DA 3.0 LE',
                              validators=[required_field('ERG'), Length(2, 80)])
    erg_da3op_re = StringField(label=u'DA OPs RE',
                                validators=[required_field('ERG'), Length(2, 80)])
    erg_da3op_le = StringField(label=u'DA OPs LE',
                                validators=[required_field('ERG'), Length(2, 80)])
    erg_la3_re = StringField(label=u'LA 3.0 RE',
                              validators=[required_field('ERG'), Length(2, 80)])
    erg_la3_le = StringField(label=u'LA 3.0 LE',
                              validators=[required_field('ERG'), Length(2, 80)])
    erg_flicker_le = StringField(label=u'30Hz Flicker LE',
                                 validators=[required_field('ERG'), Length(2, 80)])
    erg_flicker_re = StringField(label=u'30Hz Flicker RE',
                                 validators=[required_field('ERG'), Length(2, 80)])
    
    erg_comment = TextAreaField(label=u'Comment',
                                validators=[required_field('ERG')])
    
    mferg_comment = TextAreaField(label=u'mfERG comment',
                                  validators=[required_field('MFERG')])
    
    vep_comment = TextAreaField(label=u'VEP comment',
                                  validators=[required_field('VEP')])

    eog_comment = TextAreaField(label=u'EOG comment',
                                  validators=[required_field('EOG')])
    
    eog_dt_amp_re = DecimalField(label=u'Dark trough RE',
                                 description='Dark Trough amplitude RE',
                                 places=1,
                                 rounding=ROUND_HALF_UP,
                                 validators=[required_field('EOG')])
    
    eog_dt_amp_le = DecimalField(label=u'Dark trough LE',
                                 description='Dark Trough amplitude LE',
                                 places=1,
                                 rounding=ROUND_HALF_UP,
                                 validators=[required_field('EOG')])
    
    eog_lp_amp_re = DecimalField(label=u'Light peak RE',
                                 description='Light peak amplitude RE',
                                 places=1,
                                 rounding=ROUND_HALF_UP,
                                 validators=[required_field('EOG')])
    
    eog_lp_amp_le = DecimalField(label=u'Light peak LE',
                                 description='Light peak amplitude LE',
                                 places=1,
                                 rounding=ROUND_HALF_UP,
                                 validators=[required_field('EOG')])
    
    eog_lp_time_re = DecimalField(label=u'Time to light peak RE',
                                  description="Time to light peak (mins) RE",
                                  places=1,
                                 rounding=ROUND_HALF_UP,
                                  validators=[required_field('EOG')])

    eog_lp_time_le = DecimalField(label=u'Time to light peak LE',
                                  description="Time to light peak (mins) LE",
                                  places=1,
                                 rounding=ROUND_HALF_UP,
                                  validators=[required_field('EOG')])
    
    eog_ratio_re = DecimalField(label=u'LP:DT ratio RE',
                                description="LP:DT ratio RE",
                                places=2,
                                rounding=ROUND_HALF_UP,
                                validators=[required_field('EOG')])
    
    eog_ratio_le = DecimalField(label=u'LP:DT ratio LE',
                                description="LP:DT ratio LE",
                                places=2,
                                rounding=ROUND_HALF_UP,
                                validators=[required_field('EOG')])
    
    erg_submit = SubmitField('Update ERG')