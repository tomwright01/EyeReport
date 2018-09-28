# -*- coding: utf-8 -*-
from app import db
from app.imports.parse_espion_export import load_file
from app.models import Patient, Protocol, ErgParam, VepParam, MfergParam


def load_data(fname):
    """Load an espion export file"""
    file_info, data = load_file(fname)
    
    if file_info['type'] == 'mferg':
        header_info = data['params']
        visit_date_string = 'Test Date'
    elif file_info['type'] =='vep':
        header_info = data['headers']
        visit_date_string = 'Date performed'

    ptn = add_patient(header_info)    
    visit = add_visit(header_info[visit_date_string], ptn)
    protocol = get_create_protocol(file_info, header_info['Protocol'], data['stimuli'])
    test = add_test(header_info[visit_date_string], visit, protocol)
    data = get_create_data(file_info, test, data)
    db.session.commit()
    

def add_patient(header_info):
    """
    Use information in uploaded file to get or create a patient object
    Currently there is no confirmation that data is being appended to the
    correct patient. Shouldn`t cause a problem as the data is comming from exports.
    """
    dob = header_info['DOB']
    gender = header_info['Gender']
    fname = header_info.get('First Name','Anonymous')
    lname = header_info.get('Family Name','Anonymous')
    
    ptn_obj = Patient()
    ptn = ptn_obj.get_add_patient(lname=lname,
                                  fname=fname,
                                  dob=dob,
                                  gender=gender,
                                  create=True)
    return ptn        
    
def add_visit(visit_date, patient):
    visit = patient.get_add_visit(visit_date, create=True)
    return(visit)
    
def add_test(test_date, visit, protocol):
    test = visit.get_add_test(test_date, create=True)
    test.protocol = protocol
    return test

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
    db_step = test.get_add_step(data['stimuli']['description'])
    for eye in data['data'].keys():
        if eye == 'od':
            marker_idx = 0
        else:
            marker_idx = 1
            
        for i,t in enumerate(('raw','smooth')):
            channel_no = marker_idx + (i * 2) #chan 0 - od_raw, c1 - os_raw, c3 - od_smooth, c4 - os_smooth
            db_channel = db_step.get_add_channel(channel_no)
            for hex_no in range(data['params']['Hexagons']):
                hex_id = hex_no + 1
                db_result = db_channel.get_add_result(hex_id)
                db_result.add_result_timeseries(data['data'][eye][t][hex_id].start,
                                                data['data'][eye][t][hex_id].delta,
                                                data['data'][eye][t][hex_id].values,
                                                'ms', 'nV')
                marker = data['markers'][str(hex_id)][marker_idx]
                db_result.add_update_marker('N1', marker.n1[1], marker.n1[0])
                db_result.add_update_marker('P1', marker.p1[1], marker.n1[0])
    db.session.commit()
    
