import os
import shutil
from app.exceptions import EspionExportError
from flask import session, render_template, flash, redirect, request
from app import app, db
from werkzeug.utils import secure_filename
from app.forms import DataForm
from app.parse_espion_export import load_file
from tempfile import mkdtemp
from app.models import Patient, Test, Protocol, ErgParam, VepParam, MfergParam

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
            header_info = data['params']
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
        test = visit.get_add_test(header_info[visit_date_string], create=False)
        if not test:
            test = Test()
            test.visit = visit
            test.test_date = header_info[visit_date_string]
            # protocol_query = db.session.query(Protocol).filter(Protocol.name == header_info['Protocol'])
        protocol = get_create_protocol(file_info, header_info['Protocol'], data['stimuli'])
        test.protocol = protocol
        data = get_create_data(file_info, test, data)
        return redirect('/index')
        
    return render_template('store_data.html', title='Store Data', ptn=ptn)


@app.route('/patient/<id>', methods=['GET','POST'])
def patient(patient_id):
    

@app.route('/addreport/<testtype>', methods=['GET','POST'])
def addreport(testtype):
    valid_tests = ['erg','vep','mferg','perg']
    if not testtype in valid_tests:
        raise Exception('Something wrong')
        
    



def get_create_data(file_info, test, data):
    """
    Add or update time series data for a test
    """
    param_switcher = {'vep': add_vep_data,
                      'mferg': add_mferg_data}
    
    f = param_switcher[file_info['type']]
    f(test, data)

def add_vep_data(test, data):
    """
    Add time series info to a vep / erg test
    """
    
    for step_idx, step in data['data'].items():
        step_description = data['stimuli'][step_idx]['description']
        db_step = test.get_add_step(step_description)
        step_markers = data['markers'][step_idx]
        for channel_idx, channel in step.channels.items():
            db_channel = db_step.get_add_channel(channel_idx)
            channel_markers = [m for m in step_markers if m['chan'] == channel_idx]
            for result_idx, result in channel.results.items():
                result_markers = [m for m in channel_markers if m['result'] == result_idx]
                db_result = db_channel.get_add_result(result_idx)
                db_result.add_result_timeseries(result.data.start, result.data.delta, result.data.values, 'ms', 'nV')
                for marker in result_markers:
                    db_result.add_update_marker(marker['name'],
                                                marker['amp'],
                                                marker['time'],
                                                marker['amp_norm'],
                                                marker['time_norm'])
                    db_result.is_average=True
                db_timeseries = db_result.add_trial_timeseries(result.data.start, result.data.delta)
                db_timeseries.x_units = 'ms'
                db_timeseries.y_units = 'nV'
                
                for trial in result.trials:
                    db_timeseries.get_add_data(trial.values)

    db.session.commit()

def add_mferg_data(test, data):
    """
    Add time series info to an mferg test
    """
    pass

def get_stim_param(test_type, stim_params):
    if test_type == 'erg':
        param_qry = db.session.query(ErgParam).filter_by(description=stim_params['description'],
                                                         luminance=stim_params['stim'])
    elif test_type == 'vep':
        param_qry = db.session.query(VepParam).filter_by(description=stim_params['description'],
                                                         size=stim_params['stim'])
    elif test_type == 'mferg':
        param_qry = db.session.query(MfergParam).filter_by(description=stim_params['description'],
                                                           hex_count=stim_params['hex_count'])
    else:
        raise EspionExportError('Invalid test type')
    
    if param_qry.count():
        return(param_qry.first())
    else:
        pass
        
            

def get_create_protocol(file_info, protocol_name, stimuli):
    param_switcher = {'erg': create_erg_protocol,
                      'vep': create_vep_protocol,
                      'mferg': create_mferg_protocol}

    protocol_qry = db.session.query(Protocol).filter_by(name = protocol_name)
    if protocol_qry.count() < 1:
        protocol = Protocol()
        protocol.name = protocol_name
        protocol.test_class = file_info['test_type']
        db.session.add(protocol)
    else:
        protocol = protocol_qry.first()
    
    f = param_switcher.get(file_info['test_type'], None)
    f(protocol, stimuli)
    return(protocol)
        
        
def create_erg_protocol(protocol, stimuli):
    for k, stimulus in stimuli.items():
        stim_qry = db.session.query(ErgParam).filter_by(description=stimulus['description'])
        if stim_qry.count() < 1:
            stim = ErgParam()
            stim.description = stimulus['description']
            stim.luminance = stimulus['stim']
            db.session.add(stim)
        else:
            stim = stim_qry.first()
        if not stim in protocol.params:
           protocol.params.append(stim)
    db.session.commit()
           
def create_vep_protocol(protocol, stimuli):
    for k, stimulus in stimuli.items():
        stim_qry = db.session.query(VepParam).filter_by(description=stimulus['description'])
        if stim_qry.count() < 1:
            stim = VepParam()
            stim.description = stimulus['description']
            stim.size = stimulus['stim']
            db.session.add(stim)
        else:
            stim = stim_qry.first()
        if not stim in protocol.params:
           protocol.params.append(stim)

def create_mferg_protocol(protocol, stimuli):    
    stim_qry = db.session.query(MfergParam).filter_by(description=stimuli['description'])
    if stim_qry.count() < 1:
        stim = MfergParam()
        stim.description = stimuli['description']
        stim.hex_count = stimuli['hex_count']
        stim.scaled = stimuli['scaled']
        stim.distortion = stimuli['distortion']
        stim.filter = stimuli['filter']
        stim.base_period = stimuli['base_period']
        stim.correlated = stimuli['correlated']
        stim.sequence_len = stimuli['sequence_len']
        stim.smoothing_type = stimuli['smoothing_type']
        stim.smoothing_level = stimuli['smoothing_level']
        stim.filter_type = stimuli['filter_type']
        stim.filter_level = stimuli['filter_level']
        stim.filler_frames = stimuli['filler_frames']
        stim.background = stimuli['background']
        stim.color_on = stimuli['color_on']
        stim.luminance_on = stimuli['luminance_on']
        stim.color_off = stimuli['color_off']
        stim.luminance_off = stimuli['luminance_off']
        stim.notch_filter = stimuli['notch_filter']
        stim.noise_rejection_passes = stimuli['noise_rejection_passess']
        db.session.add(stim)
    else:
        stim = stim_qry.first()
    if not stim in protocol.params:
       protocol.params.append(stim)
