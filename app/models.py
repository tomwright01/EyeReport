"""
Database objects for flask patient database
"""

from app import db
from sqlalchemy.dialects import postgresql as pg

patient_diagnoses = db.Table('patient_diagnoses',
							 db.Column('patient_id', db.Integer, db.ForeignKey('patients.id')),	
							 db.Column('diagnosis_id', db.Integer, db.ForeignKey('diagnoses.id'))
							 )

visit_tests = db.Table('visit_tests',
					   db.Column('visit_id', db.Integer, db.ForeignKey('visits.id')),
					   db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
					   )
					

class Patient(db.model):
	"""
	Primary table for a patient object
	PHI is not stored here so we can apply database level security
	"""
	__tablename__ = 'patients'
	id = db.Column(db.Integer, primary_key=True)
	phi = db.relationship("PatientPHI",
						  uselist=False,
						  back_populates="patient_id")
	diagnoses = db.relationship("Diagnosis",
								secondary=patient_diagnoses,
								back_populates="patients")
	doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
	doctor = db.relationship("Doctor",
							 back_populates="patients")
	visits = db.relationship("Visit",
							 back_populates="patient")
	
class PatientPHI(db.model):
	"""
	Table for patient PHI
	"""
	__tablename__ = 'patients_phi'
	id = db.Column(db.Integer, primary_key=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
	patient = db.relationship("Patient", back_populates="phi")
	lname = db.Column(db.Unicode, length=64, nullable=False, index=True)
	fname = db.Column(db.Unicode, length=64, nullable=False)
	dob = db.Column(db.Date, nullable=False)
	__table_args__ = (db.UniqueConstraint('lname', 'fname', 'dob', name='_unique_patient'))
	
class Diagnosis(db.model):
	"""
	List of diagnoses
	"""
	__tablename__ = 'diagnoses'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Unicode, nullable=False, index=True, unique=True)
	patients = db.relationship("Patient",
							   secondary=patient_diagnoses,
							   back_populates="diagnoses")
							   
class Doctor(db.model):
	"""
	Referring doctors
	"""
	__tablename__ = 'doctors'
	id = db.Column(db.Integer, primary_key=True)
	lname = db.Column(db.Unicode, length=64, nullable=False, index=True)
	fname = db.Column(db.Unicode, length=64)
	phone = db.Column(db.Unicode, length=10)
	fax = db.Column(db.Unicode, length=10)
	email = db.Column(db.Unicode, length=128)
	patients = db.relationship("Patient", back_populates="doctor")
	__table_args__ = (db.UniqueConstraint('lname','fname', name='uc_doctor'))
	

class Visit(db.model):
	"""
	A visit is a single patient appointment, multiple tests can be performed
	"""
	__tablename__ = 'visits'
	id = db.Column(db.Integer, db.Sequence('visit_id_seq'), unique=True)
	patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
	patient = db.relationship("Patient", back_populates="visits")
	visit_date = db.Column(db.Date, nullable=False, index=True)
	notes = db.Column(db.UnicodeText)
	tests = db.relationship("Test", back_populates="visits")
	__table_args__ = (db.PrimaryKeyConstraint('patient_id','visit_date', name='pk_visit'))
	
class Test_Type(db.model):
	"""
	List of tests that could be performed
	"""
	__tablename__ = 'test_types'
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.Unicode, length=128)
	abbrv_name = db.Column(db.Unicode, length=12)
	tests = db.relationship("Test")
	
class Test(db.model):
	"""
	A test is a single procedure performed on a patient
	"""
	__tablename__ = 'tests'
	id = db.Column(db.Integer, primary_key=True)
	test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'))
	test_type = db.relationship("Test_Type", back_populates="tests")
	visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
	visit = db.relationship('Visit', back_populates="tests")
	
class TimeSeries(db.model):
	"""
	Each row is a single time series
	"""
	__tablename__ = 'timeseries'
	id = db.Column(db.Integer, primary_key=True)
	start = db.Column(db.Integer, nullable=False)
	interval = db.Column(db.Float, nullabale=False)
	x_units = db.Column(db.Unicode, nullable=False)
	y_units = db.Column(db.Unicode, nullable=False)
	data = db.relationship("TimeSeriesData")
	
class TimeSeriesData(db.model):
	"""
	Fully normalised time series data
	"""
	__tablename__ = 'timeseriesdata'
	sample = db.Column(db.Integer, nullable=False)
	value = db.Column(db.Float, nullable=False)
	timeseries_id = db.column(db.Integer, db.ForeignKey('timeseries.id'))
	
	
	
	