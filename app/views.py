import os
import shutil
from app.exceptions import EspionExportError
from flask import session, render_template, flash, redirect, request
from app import app
from werkzeug.utils import secure_filename
from app.forms import DataForm
from app.parse_espion_export import load_file
from tempfile import mkdtemp
from app.models import Patient

@app.route('/')
@app.route('/index')
def index():
    if session.get('key'):
        flash('Session value set: {}'.format(session.get('key')))
        session.pop('key')
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
        session['upload_file'] = target_file
        return redirect('/store_data')
        
    return render_template('import.html', title='Import', form=form)

@app.route('/store_data', methods=['GET','POST'])
def store_data():
    """
    Checks to see if a matching user exists.
    Stores data into the database
    """
    def clean_session():
        shutil.rmtree(os.path.abspath(os.path.dirname(session.get('upload_file'))))
        session.pop('upload_file')
        
    if not session.get('upload_file'):
        return redirect('/import')
    
    try:
        file_info, data = load_file(session.get('upload_file'))
    except EspionExportError as e:
        flash('Error: Failed to load datafile:{}'.format(e))
        clean_session()
        return redirect('import')
    
    try:
        if file_info['type'] == 'mferg':
            header_info = data['parameters']
            visit_date_string = 'Test Date'
        elif file_info['type'] =='vep':
            header_info = data['headers']
            visit_date_string = 'Date performed'
        else:
            flash('Error: files of type {} are not supported'.format(file_info['type']))
            clean_session()
            return redirect('/import')
        # order is important, dob & gender are always exported
        dob = header_info['DOB']
        gender = header_info['Gender']
        fname = header_info['First Name']
        lname = header_info['Family Name']
        
    except KeyError:
        fname = 'Anonymous'
        lname = 'Anonymous'
    ptn_obj = Patient()
    ptn = ptn_obj.get_add_patient(lname=lname,
                                  fname=fname,
                                  dob=dob,
                                  gender=gender,
                                  create=False)
    if request.args.get('confirm', None):
        if not ptn:
            # create the patient record if necessary
            ptn = ptn_obj.get_add_patient(lname=lname,
                                          fname=fname,
                                          dob=dob,
                                          gender=gender,
                                          create=True)
        # test if the visit date already exists
        visit = ptn.get_add_visit(header_info[visit_date_string], create=True)
        
        
    return render_template('store_data.html', title='Store Data', ptn=ptn)
    
    
    