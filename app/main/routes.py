# -*- coding: utf-8 -*-
from flask import render_template, flash, session, redirect, url_for

from app import db
from app.main import bp
from app.main.forms import PatientForm, PatientPhiForm, DoctorForm, DiagnosisForm
from app.main.utils import collapse_phone, format_phone
from app.models import Patient, PatientPHI, Doctor, Diagnosis

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if session.get('key'):
        flash('Session value set: {}'.format(session.get('key')))
        session.pop('key')
    return render_template('index.html', title="Home")

@bp.route('/add_patient')
def add_patient(form_ptn=None):
    """
    Accepts form_ptn as an optional variable so can pass back 
    already entered patient information if modals are used to
    add doctors or diagnosis.
    """
    if not form_ptn:
        form_ptn = PatientPhiForm()
    form_doctor = DoctorForm()
    form_diagnosis = DiagnosisForm()
    
    if form_ptn.validate_on_submit():
        ptn_phi = PatientPHI(lname=form_ptn.lname.data,
                             fname=form_ptn.fname.data,
                             dob=form_ptn.dob.data,
                             gender=form_ptn.gender.data)
        ptn_phi.patient = Patient()
        ptn_phi.patient.doctor = form_ptn.doctor.data
        ptn_phi.patient.diagnoses = form_ptn.diagnosis.data
    return render_template('edit_patient.html',
                           form=form_ptn,
                           form_adddoctor=form_doctor,
                           form_adddiagnosis=form_diagnosis)
    
@bp.route('/add_doctor', methods=['POST'])
def add_doctor():
    form = DoctorForm()
    form_ptn = PatientPhiForm()
    if form.validate_on_submit():
        phone = collapse_phone(form.phone.data)
        fax = collapse_phone(form.fax.data)
        doctor = Doctor(fname=form.fname.data,
                        lname=form.lname.data,
                        phone=phone,
                        fax=fax,
                        email=form.email.data)
        db.session.add(doctor)
        db.session.commit()
        flash('Added doctor')
    else:
        flash('Failed adding doctor')
    return redirect(url_for('main.add_patient', ptn_form=form_ptn))


@bp.route('/add_diagnosis', methods=['POST'])
def add_diagnosis():
    form = DiagnosisForm()
    form_ptn = PatientPhiForm()
    if form.validate_on_submit():
        diagnosis = Diagnosis(name=form.name.data)
        db.session.add(diagnosis)
        db.session.commit()
        flash('Added diagnosis')
    else:
        flash('Failed adding diagnosis')
    return redirect(url_for('main.add_patient', ptn_form=form_ptn))

@bp.route('/list_patients', methods=['GET'])
def list_patients():
    qry = Patient.\
        query.\
        join(PatientPHI).\
        order_by(PatientPHI.lname)
    patients = qry.all()
    return render_template('patient_list.html', patients=patients)

@bp.route('/patient/<id>')
def patient(id):
    patient = Patient.query.filter_by(id=id).first_or_404()
    return render_template('patient.html', p=patient)