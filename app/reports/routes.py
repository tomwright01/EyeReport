# -*- coding: utf-8 -*-
from flask import render_template, flash, session, request
from app.reports import bp

from app.reports.forms import ErgReport
from app.models import Report


@bp.route('/report', methods=['GET','POST'])
def report():
    form = ErgReport()
    fieldgroups = [{'name': 'da001', 'label': 'DA 0.01', 'errors': False,
                    'fields': [form.erg_da001_le,
                               form.erg_da001_re,
                               form.erg_da001_le_alt,
                               form.erg_da001_re_alt]},
                    {'name': 'da30', 'label': 'DA 3.0', 'errors': False,
                    'fields': [form.erg_da30_le,
                               form.erg_da30_re,
                               form.erg_da30_le_alt,
                               form.erg_da30_re_alt]},
                    {'name': 'da30op', 'label': 'DA 3.0 OP', 'errors': False,
                    'fields': [form.erg_da30op_le,
                               form.erg_da30op_re,
                               form.erg_da30op_le_alt,
                               form.erg_da30op_re_alt]},
                    {'name': 'la30', 'label': 'LA 3.0', 'errors': False,
                    'fields': [form.erg_la30_le,
                               form.erg_la30_re,
                               form.erg_la30_le_alt,
                               form.erg_la30_re_alt]},
                    {'name': 'flicker', 'label': '30Hz Flicker', 'errors': False,
                    'fields': [form.erg_flicker_le,
                               form.erg_flicker_re,
                               form.erg_flicker_le_alt,
                               form.erg_flicker_re_alt]}]
    
               
    if request.method=="POST":
        flash('Page Post')
    else:
        flash('Page Got')
    if form.validate_on_submit():
        report = Report()
        flash('Creating report')
        

    for fieldgroup in fieldgroups:
        for field in fieldgroup['fields']:
            if field.errors:
                fieldgroup['errors']=True
    

    return render_template('reportform.html', form=form, paramgroups=fieldgroups)
