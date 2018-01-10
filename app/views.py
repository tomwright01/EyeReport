import os
from flask import session, render_template, flash, redirect, url_for
from app import app
from werkzeug.utils import secure_filename
from app.forms import DataForm
from app.parse_export import read_export_file
from tempfile import mkdtemp

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title="Home")

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    """
    Import patient data
    """
    form = DataForm()
    
    if form.validate_on_submit():
        data = form.data_file.data
        filename = secure_filename(data.filename)
        flash('File:{} uploaded'.format(filename))
        tempdir = mkdtemp(prefix='patientDb_')
        target_file = os.path.join(tempdir, filename)
        data.save(target_file)
        flash('File saved to:{}'.format(target_file))
        data_obj = read_export_file(target_file)
        flash('Data for:{} {} uploaded.'.format(data_obj['headers']['Family Name'],
                                                data_obj['headers']['First Name']))
        
        return redirect('/index')
        
    return render_template('import.html', title='Import', form=form)