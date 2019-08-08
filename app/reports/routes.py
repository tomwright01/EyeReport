# -*- coding: utf-8 -*-
from flask import render_template, flash, session, request
from app import db
from app.reports import bp

from app.reports.forms import ErgReport
from app.models import Report

@bp.route('/test', methods=['GET'])
def test():
    return render_template('test.html')

@bp.route('/report/<visit_id>', methods=['GET','POST'])
def report(visit_id):
    
    inputText_1 = ['Within expected limits',
                   'Amplitude reduced',
                   'Amplitude reduced, delayed',
                   'Amplitude within expected limits, delayed',
                   'Not measurable above noise',
                   'Unreliable']
    
    inputText_2 = ['a-wave and b-wave within expected limits',
                   'a-wave and b-wave within expected limits, delayed',
                   'a-wave within expected limits, b-wave amplitude reduced',
                   'a-wave and b-wave amplitude reduced',
                   'a-wave and b-wave amplitude reduced, delayed',
                   'Not measurable above noise',
                   'Unreliable']
    
    inputText_ops = ['Within expected limits',
                     'Preserved, amplitude reduced',
                     'Not measurable above noise']
    
    form = ErgReport()
    erg_fieldgroups = [{'name': 'da001', 'label': 'DA 0.01', 'errors': False,
                        'fields': [form.erg_da001_le,
                                   form.erg_da001_re],
                        'inputs': inputText_1,
                        'class': "erg-input-1"},
                       {'name': 'da3', 'label': 'DA 3.0', 'errors': False,
                        'fields': [form.erg_da3_le,
                                   form.erg_da3_re],
                        'inputs': inputText_2,
                        'class': "erg-input-2"},
                       {'name': 'da3op', 'label': 'DA 3.0 OP', 'errors': False,
                        'fields': [form.erg_da3op_le,
                                   form.erg_da3op_re],
                        'inputs': inputText_ops,
                        'class': "erg-input-3"},
                       {'name': 'la3', 'label': 'LA 3.0', 'errors': False,
                        'fields': [form.erg_la3_le,
                                   form.erg_la3_re],
                        'inputs': inputText_2,
                        'class': "erg-input-2"},
                       {'name': 'flicker', 'label': '30Hz Flicker', 'errors': False,
                        'fields': [form.erg_flicker_le,
                                   form.erg_flicker_re],
                        'inputs': inputText_1,
                        'class': "erg-input-1"}]
    eog_fieldgroups = [{'name': 'dt_amp', 'label':u'Dark Trough Amp (\u00B5V / deg)',
                        'errors': False,
                        'fields': [form.eog_dt_amp_le,
                                   form.eog_dt_amp_re],
                        'class': "eog_input"},
                       {'name': 'lp_amp', 'label':u'Light Peak Amp (\u00B5V / deg)',
                        'errors': False,
                        'fields': [form.eog_lp_amp_le,
                                   form.eog_lp_amp_re],
                        'class': "eog_input"},
                       {'name': 'lp_time', 'label':u'Time to light peak (mins)',
                        'errors': False,
                        'fields': [form.eog_lp_time_le,
                                   form.eog_lp_time_re],
                        'class': "eog_input"},
                       {'name': 'ratio', 'label':u'Light Peak / Dark Trough Ratio',
                        'errors': False,
                        'fields': [form.eog_ratio_le,
                                   form.eog_ratio_re],
                        'class': "eog_input"}]
                        
    
    if form.validate_on_submit():
        db_report = Report()
        flash('Creating report')
        
        db_report.visit_id = visit_id
        db_report.information = form.information.data
        db_report.overview_comment = form.testComment.data
        
        db_report.erg_complete = form.ergComplete.data
        db_report.eog_complete = form.eogComplete.data
        db_report.vep_complete = form.vepComplete.data
        db_report.mferg_complete = form.mfergComplete.data
        
        if form.ergComplete:
            db_report.erg_da001_le = form.erg_da001_le.data
            db_report.erg_da001_re = form.erg_da001_re.data
            db_report.erg_da3_le = form.erg_da3_le.data
            db_report.erg_da3_re = form.erg_da3_re.data
            db_report.erg_da3op_le = form.erg_da3op_le.data
            db_report.erg_da3op_re = form.erg_da3op_re.data
            db_report.erg_la3_le = form.erg_la3_le.data
            db_report.erg_la3_re = form.erg_la3_re.data
            db_report.erg_flicker_le = form.erg_flicker_le.data
            db_report.erg_flicker_re = form.erg_flicker_re.data
            db_report.erg_comment = form.erg_comment.data

        if form.mfergComplete:
            db_report.mferg_comment = form.mferg_comment.data

        if form.vepComplete:
            db_report.vep_comment = form.vep_comment.data

        if form.eogComplete:
            db_report.eog_dt_amp_le = form.eog_dt_amp_le.data
            db_report.eog_dt_amp_re = form.eog_dt_amp_re.data
            db_report.eog_lp_amp_le = form.eog_lp_amp_le.data
            db_report.eog_lp_amp_re = form.eog_lp_amp_re.data
            db_report.eog_lp_time_le = form.eog_lp_time_le.data
            db_report.eog_lp_time_re = form.eog_lp_time_re.data
            db_report.eog_ratio_le = form.eog_ratio_le.data
            db_report.eog_ratio_re = form.eog_ratio_re.data
            db_report.eog_comment = form.eog_comment.data
    
        db.session.add(db_report)
        db.session.commit()
    elif request.method == 'GET':
        db_report = Report.query.filter_by(visit_id=visit_id).first()
        if db_report:
            form.information.data = db_report.information
            form.testComment.data = db_report.overview_comment
            
            form.ergComplete.data = db_report.erg_complete
            form.mfergComplete.data = db_report.mferg_complete
            form.vepComplete.data = db_report.vep_complete
            form.eogComplete.data = db_report.eog_complete
            form.mfergComplete.data = db_report.mferg_complete
            
            if db_report.erg_complete:
                form.erg_da001_le.data = db_report.erg_da001_le
                form.erg_da001_re.data = db_report.erg_da001_re
                form.erg_da3_le.data = db_report.erg_da3_le
                form.erg_da3_re.data = db_report.erg_da3_re
                form.erg_da3op_le.data = db_report.erg_da3op_le
                form.erg_da3op_re.data = db_report.erg_da3op_re
                form.erg_la3_le.data = db_report.erg_la3_le
                form.erg_la3_re.data = db_report.erg_la3_re
                form.erg_flicker_le.data = db_report.erg_flicker_le
                form.erg_flicker_re.data = db_report.erg_flicker_re
            
            if db_report.mferg_complete:
                form.mferg_comment.data = db_report.mferg_comment
                
            if db_report.vep_complete:
                form.vep_comment.data = db_report.vep_comment
                
            if db_report.eog_complete:
                form.eog_comment.data = db_report.eog_comment
                form.eog_dt_amp_le.data = db_report.eog_dt_amp_le
                form.eog_dt_amp_re.data = db_report.eog_dt_amp_re
                form.eog_lp_amp_le.data = db_report.eog_lp_amp_le
                form.eog_lp_amp_re.data = db_report.eog_lp_amp_re
                form.eog_lp_time_le.data = db_report.eog_lp_time_le
                form.eog_lp_time_re.data = db_report.eog_lp_time_re
                form.eog_ratio_le.data = db_report.eog_ratio_le
                form.eog_ratio_re.data = db_report.eog_ratio_re
                
    for fieldgroup in erg_fieldgroups:
        for field in fieldgroup['fields']:
            if field.errors:
                assert 1==2
                fieldgroup['errors']=True
    
    
    return render_template('reportform.html', form=form, paramgroups={'erg': erg_fieldgroups,
                                                                      'eog': eog_fieldgroups})
