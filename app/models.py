"""
Database objects for flask patient database
"""

from app import db
from sqlalchemy.dialects import postgresql as pg
import datetime
import logging

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
protocol_steps_vep = db.Table('protocol_steps_erg',
                              db.Column('protocol_id', db.Integer, db.ForeignKey('protocols.id')),
                              db.Column('erg_param_id', db.Integer, db.ForeignKey('erg_params.id'))
                              )
protocol_steps_mferg = db.Table('protocol_steps_erg',
                                db.Column('protocol_id', db.Integer, db.ForeignKey('protocols.id')),
                                db.Column('erg_param_id', db.Integer, db.ForeignKey('erg_params.id'))
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

    def get_add_patient(self, lname, fname, dob, gender, create=False):
        """
        Search for a patient using PHI, returns a Patient object
        if PatientPHI is not found, and add==True creates a new patient objects
        """
        assert isinstance(dob, datetime.date), 'dob must be a date object'
        pat_phi = PatientPHI.query.filter_by(fname=fname,
                                             lname=lname,
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
        db.session.commit()
        return(self)

    def get_add_visit(self, visit_date, create=False):
        assert isinstance(visit_date, datetime.date), 'Visit date must be a date object.'
        for visit in self.visits:
            if visit.visit_date == visit_date:
                return(visit)
        if not create:
            logger.debug('Visit date:{} for Subject:{} not found, Create is false, not creating'
                         .format(visit_date.strftime('%Y-%m-%d'), self.id))
            return(None)
        visit = Visit()
        visit.patient = self
        visit.visit_date = visit_date
        db.session.add(visit)
        db.session.commit()
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

class Visit(db.Model):
    """
    A visit is a single patient appointment, multiple tests can be performed
    """
    __tablename__ = 'visits'
    id = db.Column(db.Integer, db.Sequence('visit_id_seq'), unique=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    patient = db.relationship("Patient", back_populates="visits")
    visit_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.UnicodeText)
    tests = db.relationship("Test",
                            secondary=visit_tests,
                            back_populates="visits")
    __table_args__ = (db.PrimaryKeyConstraint('patient_id','visit_date', name='pk_visit'),)
    
    def get_add_test(self, protocol_name, create=False):
        for test in self.tests:
            if test.protocol.test_type.fullname == protocol_name:
                return(test)

class Test_Type(db.Model):
    """
    List of tests that could be performed
    """
    __tablename__ = 'test_types'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.Unicode(128))
    abbrv_name = db.Column(db.Unicode(12))
    test_class = db.Column(db.Enum('mferg', 'vep', 'perg', 'eog', name='test_class'), nullable=False)
    tests = db.relationship("Test")

class Test(db.Model):
    """
    A test is a single test type (ERG, mfERG, etc.) carried out at a visit.
    Each Test has an associated protocol that defines the steps.
    """
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    visit = db.relationship('Visit', back_populates="tests")    
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'))
    protocol = db.relationship('Protocol', back_populates="tests")
    visits = db.relationship("Visit",
                             secondary=visit_tests,
                             back_populates="tests")
    
class Protocol(db.Model):
    """
    A test is a single procedure performed on a patient
    Each protocol consists of a series of stimuli.
    """
    __tablename__ = 'protocols'
    id = db.Column(db.Integer, primary_key=True)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'))
    test_type = db.relationship("Test_Type", back_populates="tests")
    erg_steps = db.relationship("erg_steps",
                                secondary=protocol_steps_erg,
                                back_populates="protocol")
    vep_steps = db.relationship("vep_steps",
                                secondary=protocol_steps_vep,
                                back_populates="protocol")
    mferg_steps = db.relationship("erg_steps",
                                  secondary=protocol_steps_mferg,
                                  back_populates="protocol")
class TimeSeries(db.Model):
    """
    Each row is a single time series
    """
    __tablename__ = 'timeseries'
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Float, nullable=False)
    x_units = db.Column(db.Unicode, nullable=False)
    y_units = db.Column(db.Unicode, nullable=False)
    data = db.relationship("TimeSeriesData", back_populates="timeseries")

class TimeSeriesData(db.Model):
    """
    Fully normalised time series data
    """
    __tablename__ = 'timeseriesdata'
    id = db.Column(db.Integer, primary_key=True)
    sample = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    timeseries_id = db.Column(db.Integer, db.ForeignKey('timeseries.id'))
    timeseries = db.relationship('TimeSeries', back_populates="data")

class MfergParams(db.Model):
    """
    Stimulus parameters for mfERG type tests
    """
    __tablename__ = 'mferg_params'
    id = db.Column(db.Integer, primary_key=True)
    hex_count = db.Column(db.Integer, nullable=False)
    scaled = db.Column(db.Boolean, nullable=False)
    distortion = db.Column(db.Unicode)
    filter = db.Column(db.Unicode)
    base_period = db.Column(db.Float)
    correlated = db.Column(db.Float)
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
    
class VepParams(db.Model):
    """
    Stimulus parameters for VEP type tests
    """
    __tablename__ = 'vep_params'
    description = db.Column(db.Unicode)
    size = db.Column(db.float, nullable=False)
    eye = db.Column(db.Enum('left' ,'right', 'binocular', 'none', name='vep_eye_tested'))
    
class ErgParams(db.Model):
    
     """
     Stimulus parameters for ERG type tests
     """
     __tablename__ = 'erg_params'
     description = db.Column(db.Unicode, nullable=False)
     luminance = db.Column(db.Float, nullable=False)


     
    
    
    