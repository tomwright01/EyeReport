"""
Database objects for flask patient database
"""

from app import db
from sqlalchemy.dialects import postgresql as pg
import datetime

patient_diagnoses = db.Table('patient_diagnoses',
                             db.Column('patient_id', db.Integer, db.ForeignKey('patients.id')),
                             db.Column('diagnosis_id', db.Integer, db.ForeignKey('diagnoses.id'))
                             )

visit_tests = db.Table('visit_tests',
                       db.Column('visit_id', db.Integer, db.ForeignKey('visits.id')),
                       db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
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

    def get_add_patient(lname, fname, dob, gender, create=False):
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
            return()

        if not create:
            logger.debug('Requested patient: {} {} not found. Create is false, not creating'
                         .format(fname, lname))
            return(None)

        pat_phi = PatientPhi()
        pat_phi.lname = lname.upper()
        pat_phi.fname = fname.upper()
        pat_phi.dob = dob
        pat_phi.gender = gender.lower()
        self.phi = pat_phi
        return(self)

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
    tests = db.relationship("Test", back_populates="visit")
    __table_args__ = (db.PrimaryKeyConstraint('patient_id','visit_date', name='pk_visit'),)

class Test_Type(db.Model):
    """
    List of tests that could be performed
    """
    __tablename__ = 'test_types'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.Unicode(128))
    abbrv_name = db.Column(db.Unicode(12))
    tests = db.relationship("Test")

class Test(db.Model):
    """
    A test is a single procedure performed on a patient
    """
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'))
    test_type = db.relationship("Test_Type", back_populates="tests")
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    visit = db.relationship('Visit', back_populates="tests")

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
