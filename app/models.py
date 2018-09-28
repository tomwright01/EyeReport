"""
Database objects for flask patient database
"""

from app import db
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.ext.hybrid import hybrid_property
import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)

patient_diagnoses = db.Table('patient_diagnoses',
                             db.Column('patient_id', db.Integer, db.ForeignKey('patients.id')),
                             db.Column('diagnosis_id', db.Integer, db.ForeignKey('diagnoses.id'))
                             )

visit_tests = db.Table('visit_tests',
                       db.Column('visit_id', db.Integer, db.ForeignKey('visits.id')),
                       db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
                       )

protocol_steps_erg = db.Table('protocol_steps_erg',
                              db.Column('protocol_id', db.Integer, db.ForeignKey('protocols.id')),
                              db.Column('erg_param_id', db.Integer, db.ForeignKey('erg_params.id'))
                              )
protocol_steps_vep = db.Table('protocol_steps_vep',
                              db.Column('protocol_id', db.Integer, db.ForeignKey('protocols.id')),
                              db.Column('vep_param_id', db.Integer, db.ForeignKey('vep_params.id'))
                              )
protocol_steps_mferg = db.Table('protocol_steps_mferg',
                                db.Column('protocol_id', db.Integer, db.ForeignKey('protocols.id')),
                                db.Column('mferg_param_id', db.Integer, db.ForeignKey('mferg_params.id'))
                              )
timeseries_timeseriesdata = db.Table('timeseries_timeseriesdata', 
                                     db.Column('timeseries_id', db.Integer, db.ForeignKey('timeseries.id')),
                                     db.Column('timeseriesdata_id', db.Integer, db.ForeignKey('timeseriesdata.id'))
                                     )
class Patient(db.Model):
    """
    Primary table for a patient object
    PHI is not stored here so we can apply database level security
    """
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    phi = db.relationship("PatientPHI",
                          uselist=False,
                          back_populates="patient")
    diagnoses = db.relationship("Diagnosis",
                                secondary=patient_diagnoses,
                                back_populates="patients")
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    doctor = db.relationship("Doctor",
                             back_populates="patients")
    visits = db.relationship("Visit",
                             back_populates="patient")
    tests = db.relationship("Test",
                            back_populates="patient")

    def get_add_patient(self, lname, fname, dob, gender, create=False):
        """
        Search for a patient using PHI, returns a Patient object
        if PatientPHI is not found, and add==True creates a new patient objects
        """
        assert isinstance(dob, datetime.date), 'dob must be a date object'
        pat_phi = PatientPHI.query.filter_by(fname=fname.upper(),
                                             lname=lname.upper(),
                                             dob=dob).first()
        if pat_phi:
            self = pat_phi.patient
            return(self)

        if not create:
            logger.debug('Requested patient: {} {} not found. Create is false, not creating'
                         .format(fname, lname))
            return(None)

        pat_phi = PatientPHI()
        pat_phi.lname = lname.upper()
        pat_phi.fname = fname.upper()
        pat_phi.dob = dob
        pat_phi.gender = gender.lower()
        self.phi = pat_phi
        db.session.add(self)
        
        return(self)

    def get_add_visit(self, visit_date, create=False):
        assert isinstance(visit_date, datetime.date), 'Visit date must be a date object.'
        for visit in self.visits:
            if visit.visit_date.strftime('%Y-%m-%d') == visit_date.strftime('%Y-%m-%d'):
                return(visit)
        if not create:
            logger.debug('Visit date:{} for Subject:{} not found, Create is false, not creating'
                         .format(visit_date.strftime('%Y-%m-%d'), self.id))
            return(None)
        visit = Visit()
        visit.patient = self
        visit.visit_date = visit_date
        db.session.add(visit)
        return(visit)
                

        
class PatientPHI(db.Model):
    """
    Table for patient PHI
    """
    __tablename__ = 'patients_phi'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    patient = db.relationship("Patient", back_populates="phi")
    lname = db.Column(db.Unicode(64), nullable=False, index=True)
    fname = db.Column(db.Unicode(64), nullable=False)
    gender = db.Column(db.Enum('male','female', name='gender_types'))
    dob = db.Column(db.Date, nullable=False)
    __table_args__ = (db.UniqueConstraint('lname', 'fname', 'dob', name='_unique_patient'),)

class Diagnosis(db.Model):
    """
    List of diagnoses
    """
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False, index=True, unique=True)
    patients = db.relationship("Patient",
                               secondary=patient_diagnoses,
                               back_populates="diagnoses")

def get_diagnosis():
    return Diagnosis.query

class Doctor(db.Model):
    """
    Referring doctors
    """
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.Unicode(64), nullable=False, index=True)
    fname = db.Column(db.Unicode(64))
    phone = db.Column(db.Unicode(10))
    fax = db.Column(db.Unicode(10))
    email = db.Column(db.Unicode(128))
    patients = db.relationship("Patient", back_populates="doctor")
    __table_args__ = (db.UniqueConstraint('lname','fname', name='uc_doctor'),)
    
    @property
    def formatted_name(self):
        return('Dr. {}. {}'.format(self.fname[0], self.lname))

def get_doctors():
    return Doctor.query

class Visit(db.Model):
    """
    A visit is a single patient appointment, multiple tests can be performed
    """
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    patient = db.relationship("Patient", back_populates="visits")
    visit_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.UnicodeText)
    tests = db.relationship("Test", back_populates="visit")
    report = db.relationship("Report", back_populates="visit")
    __table_args__ = (db.UniqueConstraint('patient_id','visit_date', name='pk_visit'),)
    
    def get_add_test(self, test_date, create=False):
        """
        Identifies a test by date time
        """
        assert isinstance(test_date, datetime.datetime), "Must supply a datetime object"
        for test in self.tests:
            if test.test_date == test_date:
                return(test)
        if not create:
            logger.debug('Test date:{} not found for visit id:{}, creeate false, skipping'
                         .format(test_date.strftime('%Y-%m-%d:%H:%m'),
                                 self.id))
            return(None)
        test = Test()
        test.patient = self.patient
        test.test_date = test_date
        test.visit = self
        db.session.add(test)
        return(test)

#class Test_Type(db.Model):
#    """
#    List of tests that could be performed
#    """
#    __tablename__ = 'test_types'
#    id = db.Column(db.Integer, primary_key=True)
#    fullname = db.Column(db.Unicode(128))
#    abbrv_name = db.Column(db.Unicode(12))
#    test_class = db.Column(db.Enum('mferg', 'vep', 'perg', 'eog', name='test_class'), nullable=False)
#    tests = db.relationship("Test", back_populates="test_type")
#    protocols = db.relationship("Protocol", back_populates="test_type")

       
class Step(db.Model):
    """
    A step consists of a particular stimulus, each step can have multiple timeseries
    As a step can be only one type, and different types have different stimulus parameters
    the stimulus parameters should only be accessed throught he param property.
    """
    __tablename__ = 'steps'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    test = db.relationship('Test', back_populates="steps")
    mferg_param_id = db.Column(db.Integer, db.ForeignKey('mferg_params.id'))
    mferg_param = db.relationship('MfergParam', back_populates='steps')
    erg_param_id = db.Column(db.Integer, db.ForeignKey('erg_params.id'))
    erg_param = db.relationship('ErgParam', back_populates="steps")
    vep_param_id = db.Column(db.Integer, db.ForeignKey('vep_params.id'))
    vep_param = db.relationship('VepParam', back_populates="steps")
    channels = db.relationship('StepChannel', back_populates = "step")
    
    
    @hybrid_property
    def param(self):
        test_class = self.test.protocol.test_class
        if test_class == 'mferg':
            return(self.mferg_param)
        elif test_class == 'vep':
            return(self.vep_param)
        elif test_class == 'erg':
            return(self.erg_param)
        else:
            raise ValueError('Test class:{} not defined.'.format(test_class))

    @param.setter
    def param(self, param_obj):
        test_class = self.test.protocol.test_class
        if isinstance(param_obj, MfergParam):
            if not test_class == 'mferg':
                raise ValueError('These parameters are not valid for this test type')
            self.mferg_param = param_obj
        elif isinstance(param_obj, ErgParam):
            if not test_class == 'erg':
                raise ValueError('These parameters are not valid for this test type')
            self.erg_param = param_obj
        elif isinstance(param_obj, VepParam):
            if not test_class == 'vep':
                raise ValueError('These parameters are not valid for this test type')
            self.vep_param = param_obj
        else:
            assert 1==2
            raise ValueError('Parameter class not defined')

    def get_add_channel(self, channel_no):
        c = next((channel for channel in self.channels if channel.channel_no == channel_no), None)
        if not c:
            c = StepChannel()
            c.channel_no = channel_no
            c.step = self
            db.session.add(c)
        return c
    
class StepChannel(db.Model):
    """
    A single channel recording of a step
    each channel can have multiple results
    """
    __tablename__ = 'step_channel'
    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'))
    step = db.relationship('Step', back_populates="channels")
    channel_no = db.Column(db.Integer, nullable=False)
    results = db.relationship('Result', back_populates="channel")
    db.UniqueConstraint(step_id, channel_no, name='stepchannel_pk')
    
    @hybrid_property
    def channel_name(self):
        if self.step.test.protocol.protocol_class == 'mferg':
            names = {1: 'RE_raw', 2: 'LE_raw', 3: 'RE_smooth', 4: 'LE_smooth'}
        else:
            names = {1: 'RE', 2: 'LE', 3: 'RE_OP', 4: 'LE_OP'}
        try:
            return(names[self.channel_no])
        except KeyError:
            raise ValueError('Channel number not defined')
    
    @channel_name.setter
    def channel_name(self, name):
        if self.step.test.protocol.protocol_class == 'mferg':
            names = {'RE_raw': 1, 'LE_raw': 2,'RE_smooth': 3, 'LE_smooth': 4}
        else:
            names = {'RE': 1, 'LE': 2,'RE_OP': 3, 'LE_OP': 4}

        try:
            self.channel_no = names[name.upper()]
        except KeyError:
            raise ValueError('Invalid channel:{}'.format(name))
            
    def get_add_result(self, result_no):
        r = next((r for r in self.results if r.result_no == result_no), None)
        if not r:
            r=Result()
            r.channel = self
            r.result_no = result_no
            db.session.add(r)
        return r
        
class Result(db.Model):
    """
    Each result is owned by a StepChannel
    Each result can have a single time series.
    
    In the case of an mfERG each result represents a hexagon, result_no contains the hex_id
    """
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    result_no = db.Column(db.Integer, nullable=False)
    is_average = db.Column(db.Boolean, nullable=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('step_channel.id'))
    channel = db.relationship('StepChannel', back_populates="results")
    time_series = db.relationship('TimeSeries', uselist=False, back_populates = "result")
    result_data = db.relationship('TimeSeries', uselist=False)
    markers = db.relationship('Marker', back_populates = "result")
    db.UniqueConstraint(channel_id, result_no, name='results_pk')
    
    def add_result_timeseries(self, start, delta, data, x_unit, y_unit):
        if not self.result_data:
            self.result_data = TimeSeries()
            db.session.add(self.result_data)
        self.result_data.start = start
        self.result_data.interval = delta
        self.result_data.x_units = x_unit
        self.result_data.y_units = y_unit
        self.result_data.is_trial = False
        with db.session.no_autoflush:
            self.result_data.get_add_data(data)
        
    
    def add_trial_timeseries(self, start, delta):
        if self.time_series:
            return self.time_series
        ts = TimeSeries()
        ts.result = self
        ts.start = start
        ts.interval = delta
        ts.is_trial = True
        db.session.add(ts)
        return(ts)
        
    def add_update_marker(self, name, amp, timing, amp_range = [None,None], it_range =[None,None]):
        m = next((m for m in self.markers if m.name==name), None)
        if not m:
            m=Marker()
            m.name = name
            self.markers.append(m)
            db.session.add(m)
        m.amp = amp
        m.it = timing
        if not all(x is None for x in amp_range):
            m.amp_normal_min=amp_range[0]
            m.amp_normal_max=amp_range[1]
        if not all(x is None for x in it_range):
            m.it_normal_min=it_range[0]
            m.it_normal_max=it_range[1]
        
        
    
    
class Report(db.Model):
    """
    Information on a report, one to one relationship with visits
    """
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    visit = db.relationship('Visit', back_populates='report')
    information = db.Column(db.UnicodeText)
    erg_da001_re = db.Column(db.Unicode(80))
    erg_da001_le = db.Column(db.Unicode(80))
    erg_da3_re = db.Column(db.Unicode(80))
    erg_da3_le = db.Column(db.Unicode(80))
    erg_da3op_re = db.Column(db.Unicode(80))
    erg_da3op_le = db.Column(db.Unicode(80))
    erg_la3_re = db.Column(db.Unicode(80))
    erg_la3_le = db.Column(db.Unicode(80))
    erg_flicker_re = db.Column(db.Unicode(80))
    erg_flicker_le = db.Column(db.Unicode(80))
    erg_phnr_re = db.Column(db.Unicode(80))
    erg_phnr_le = db.Column(db.Unicode(80))
    erg_comment = db.Column(db.UnicodeText)
    mferg_comment = db.Column(db.UnicodeText)
    perg_comment = db.Column(db.UnicodeText)
    fvep_comment = db.Column(db.UnicodeText)
    pvep_comment = db.Column(db.UnicodeText)
    overview_comment = db.Column(db.UnicodeText)
    
    

class Protocol(db.Model):
    """
    A test is a single procedure performed on a patient
    Each protocol consists of a series of stimuli.
    """
    __tablename__ = 'protocols'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128), nullable=False, unique=True)
    test_class = db.Column(db.Enum('mferg', 'vep', 'perg', 'eog', 'erg', name='test_class'), nullable=False)
    tests = db.relationship("Test", back_populates="protocol")
    erg_params = db.relationship("ErgParam",
                                secondary=protocol_steps_erg,
                                back_populates="protocols")
    vep_params = db.relationship("VepParam",
                                secondary=protocol_steps_vep,
                                back_populates="protocols")
    mferg_params = db.relationship("MfergParam",
                                  secondary=protocol_steps_mferg,
                                  back_populates="protocols")

    @hybrid_property
    def params(self):
        test_class = self.test_class
        if test_class == 'mferg':
            return(self.mferg_params)
        elif test_class == 'vep':
            return(self.vep_params)
        elif test_class == 'erg':
            return(self.erg_params)
        else:
            raise ValueError('Test class:{} not defined.'.format(test_class))

    @params.setter
    def params(self, param_obj):
        test_class = self.test_class
        if isinstance(param_obj, MfergParam):
            if not test_class == 'mferg':
                raise ValueError('These parameters are not valid for this test type')
            self.mferg_param = param_obj
        elif isinstance(param_obj, ErgParam):
            if not test_class == 'erg':
                raise ValueError('These parameters are not valid for this test type')
            self.erg_param = param_obj
        elif isinstance(param_obj, VepParam):
            if not test_class == 'vep':
                raise ValueError('These parameters are not valid for this test type')
            self.vep_param = param_obj
        else:
            raise ValueError('Parameter class not defined')


class Test(db.Model):
    """
    A test is a single test type (ERG, mfERG, etc.) carried out at a visit.
    Each test can consist of multiple steps defined in the protocol
    """
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    test_date = db.Column(db.DateTime, nullable=False, index=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    visit = db.relationship('Visit', back_populates="tests")    
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    patient = db.relationship('Patient', back_populates="tests")
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'))
    protocol = db.relationship('Protocol', back_populates="tests")
    steps = db.relationship("Step", back_populates="test")

    def get_add_step(self, step_description):
        """returns a step with protocol with description"""
        s = next((step for step in self.steps if step.param.description == step_description), None)
        if not s:
            #step doesn't exist yet, need to create a new one
            p = next((param for param in self.protocol.params if param.description == step_description), None)
            if not p:
                raise ValueError('step_description:{} not defined'.format(step_description))
            s = Step()
            s.test = self
            s.param = p
            db.session.add(s)
        return s


class TimeSeries(db.Model):
    """
    A time series can hold multiple trials
    """
    __tablename__ = 'timeseries'
    id = db.Column(db.Integer, primary_key=True)
    is_trial = db.Column(db.Boolean, nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey("results.id"))
    result = db.relationship("Result", back_populates="time_series")
    start = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Numeric, nullable=False)
    x_units = db.Column(db.Unicode, nullable=False)
    y_units = db.Column(db.Unicode, nullable=False)
    data_id = db.Column(db.Integer, db.ForeignKey("timeseriesdata.id"))
    data = db.relationship("TimeSeriesData",
                           secondary = timeseries_timeseriesdata,
                           back_populates="timeseries")
    
    def get_add_data(self, data):
        """
        Writes data as postgres array, much faster
        """
        hash_str = hashlib.sha256(str(data).encode('utf-8')).hexdigest()
        # check if TS is already attached, if yes we can just return it
        d = next((tsd for tsd in self.data if tsd.hash_str == hash_str), None)
        if not d:
            # see if data already exists in the db
            q = db.session.query(TimeSeriesData).filter(TimeSeriesData.hash_str == hash_str)

            if q.count():
                d = q.first()
            else:
                # doesnt exist create a new one
                d=TimeSeriesData()
                db.session.add(d)
                d.values = data
                d.hash_str = hash_str
            self.data.append(d)
        return d


class Marker(db.Model):
    """
    Marker data        
    """
    __tablename__ = 'markers'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey("results.id"))
    result = db.relationship("Result", back_populates="markers")
    name = db.Column(db.Unicode, nullable=False)
    amp = db.Column(db.Numeric, nullable=True)
    it = db.Column(db.Numeric, nullable=False)
    
    amp_normal_min = db.Column(db.Numeric)
    amp_normal_max = db.Column(db.Numeric)
    it_normal_min = db.Column(db.Numeric)
    it_normal_max = db.Column(db.Numeric)
    
    
class TimeSeriesData(db.Model):
    """
    Timeseries data, not normalised
    """
    __tablename__ = 'timeseriesdata'
    id = db.Column(db.Integer, primary_key=True)
    timeseries = db.relationship('TimeSeries',
                                 secondary=timeseries_timeseriesdata,
                                 back_populates="data")
    values = db.Column(db.ARRAY(db.Numeric))
    hash_str = db.Column(db.Unicode, nullable=False)
    db.Index('idx_data_hash', hash_str, unique=True)

class MfergParam(db.Model):
    """
    Stimulus parameters for mfERG type tests
    """
    __tablename__ = 'mferg_params'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Unicode)
    hex_count = db.Column(db.Integer, nullable=False)
    scaled = db.Column(db.Boolean, nullable=False)
    distortion = db.Column(db.Unicode)
    filter = db.Column(db.Unicode)
    base_period = db.Column(db.Numeric)
    correlated = db.Column(db.Numeric)
    sequence_len = db.Column(db.Integer, nullable=False)
    smoothing_type = db.Column(db.Enum('average', name='mferg_smoothing_type'))
    smoothing_level = db.Column(db.Integer, nullable=False)
    filter_type = db.Column(db.Enum('adaptive', 'fft', name='mferg_filter_type'))
    filter_level = db.Column(db.Integer, nullable=False)
    filler_frames = db.Column(db.Integer)
    background = db.Column(db.Enum('mean luminance', name='mferg_background_type'))
    color_on = db.Column(db.Unicode)
    luminance_on = db.Column(db.Integer)
    color_off = db.Column(db.Unicode)
    luminance_off = db.Column(db.Integer)
    notch_filter = db.Column(db.Boolean)
    noise_rejection_passes = db.Column(db.Integer)
    steps = db.relationship("Step", back_populates="mferg_param")
    protocols = db.relationship("Protocol",
                                secondary=protocol_steps_mferg,
                                back_populates="mferg_params")
    
class VepParam(db.Model):
    """
    Stimulus parameters for VEP type tests
    """
    __tablename__ = 'vep_params'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Unicode)
    size = db.Column(db.Numeric, nullable=False)
    eye = db.Column(db.Enum('left' ,'right', 'binocular', 'none', name='vep_eye_tested'))
    steps = db.relationship("Step", back_populates="vep_param")
    protocols = db.relationship("Protocol",
                                secondary=protocol_steps_vep,
                                back_populates="vep_params")
    
class ErgParam(db.Model):
    
     """
     Stimulus parameters for ERG type tests
     """
     __tablename__ = 'erg_params'
     id = db.Column(db.Integer, primary_key=True)
     description = db.Column(db.Unicode, nullable=False)
     luminance = db.Column(db.Numeric, nullable=False)
     steps = db.relationship("Step", back_populates="erg_param")
     protocols = db.relationship("Protocol",
                                secondary=protocol_steps_erg,
                                back_populates="erg_params")


     
    
    
    