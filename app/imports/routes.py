# -*- coding: utf-8 -*-
import os
from tempfile import mkdtemp
from werkzeug.utils import secure_filename

from flask import render_template, redirect, flash, session

from app.imports import bp
from app.imports.store import load_data

from app.imports.forms import DataForm

@bp.route('/import', methods=['GET', 'POST'])
def upload_data():
    """
    Upload a patient datafile,
    Creates a server side copy of the data
    """
    form = DataForm()
    
    if form.validate_on_submit():
        data = form.data_file.data
        filename = secure_filename(data.filename)
        flash('File:{} uploaded'.format(filename))
        tempdir = mkdtemp(prefix='patientDb_')
        target_file = os.path.join(tempdir, filename)
        data.save(target_file)
        session['upload_file'] = target_file
        load_data(target_file)
        
    return render_template('import.html', title='Import', form=form)
