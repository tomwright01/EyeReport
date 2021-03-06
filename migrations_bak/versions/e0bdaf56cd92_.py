"""empty message

Revision ID: e0bdaf56cd92
Revises: 
Create Date: 2018-11-06 11:14:43.565858

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e0bdaf56cd92'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diagnoses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnoses_name'), 'diagnoses', ['name'], unique=True)
    op.create_table('doctors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lname', sa.Unicode(length=64), nullable=False),
    sa.Column('fname', sa.Unicode(length=64), nullable=True),
    sa.Column('phone', sa.Unicode(length=10), nullable=True),
    sa.Column('fax', sa.Unicode(length=10), nullable=True),
    sa.Column('email', sa.Unicode(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lname', 'fname', name='uc_doctor')
    )
    op.create_index(op.f('ix_doctors_lname'), 'doctors', ['lname'], unique=False)
    op.create_table('erg_params',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Unicode(), nullable=False),
    sa.Column('luminance', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('markers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Unicode(), nullable=False),
    sa.Column('amp', sa.Numeric(), nullable=True),
    sa.Column('it', sa.Numeric(), nullable=False),
    sa.Column('amp_normal_min', sa.Numeric(), nullable=True),
    sa.Column('amp_normal_max', sa.Numeric(), nullable=True),
    sa.Column('it_normal_min', sa.Numeric(), nullable=True),
    sa.Column('it_normal_max', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mferg_params',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Unicode(), nullable=True),
    sa.Column('hex_count', sa.Integer(), nullable=False),
    sa.Column('scaled', sa.Boolean(), nullable=False),
    sa.Column('distortion', sa.Unicode(), nullable=True),
    sa.Column('filter', sa.Unicode(), nullable=True),
    sa.Column('base_period', sa.Numeric(), nullable=True),
    sa.Column('correlated', sa.Numeric(), nullable=True),
    sa.Column('sequence_len', sa.Integer(), nullable=False),
    sa.Column('smoothing_type', sa.Enum('average', name='mferg_smoothing_type'), nullable=True),
    sa.Column('smoothing_level', sa.Integer(), nullable=False),
    sa.Column('filter_type', sa.Enum('adaptive', 'fft', name='mferg_filter_type'), nullable=True),
    sa.Column('filter_level', sa.Integer(), nullable=False),
    sa.Column('filler_frames', sa.Integer(), nullable=True),
    sa.Column('background', sa.Enum('mean luminance', name='mferg_background_type'), nullable=True),
    sa.Column('color_on', sa.Unicode(), nullable=True),
    sa.Column('luminance_on', sa.Integer(), nullable=True),
    sa.Column('color_off', sa.Unicode(), nullable=True),
    sa.Column('luminance_off', sa.Integer(), nullable=True),
    sa.Column('notch_filter', sa.Boolean(), nullable=True),
    sa.Column('noise_rejection_passes', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient_diagnoses',
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('diagnosis_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], )
    )
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patients_phi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('lname', sa.Unicode(length=64), nullable=False),
    sa.Column('fname', sa.Unicode(length=64), nullable=False),
    sa.Column('gender', sa.Enum('male', 'female', name='gender_types'), nullable=True),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lname', 'fname', 'dob', name='_unique_patient')
    )
    op.create_index(op.f('ix_patients_phi_lname'), 'patients_phi', ['lname'], unique=False)
    op.create_table('protocol_steps_erg',
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.Column('erg_param_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['erg_param_id'], ['erg_params.id'], ),
    sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], )
    )
    op.create_table('protocol_steps_mferg',
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.Column('mferg_param_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['mferg_param_id'], ['mferg_params.id'], ),
    sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], )
    )
    op.create_table('protocol_steps_vep',
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.Column('vep_param_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], ),
    sa.ForeignKeyConstraint(['vep_param_id'], ['vep_params.id'], )
    )
    op.create_table('protocols',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=128), nullable=False),
    sa.Column('test_class', sa.Enum('mferg', 'vep', 'perg', 'eog', 'erg', name='test_class'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('visit_id', sa.Integer(), nullable=True),
    sa.Column('information', sa.UnicodeText(), nullable=True),
    sa.Column('erg_da001_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_da001_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_da3_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_da3_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_da3op_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_da3op_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_la3_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_la3_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_flicker_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_flicker_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_phnr_re', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_phnr_le', sa.Unicode(length=80), nullable=True),
    sa.Column('erg_comment', sa.UnicodeText(), nullable=True),
    sa.Column('mferg_comment', sa.UnicodeText(), nullable=True),
    sa.Column('perg_comment', sa.UnicodeText(), nullable=True),
    sa.Column('fvep_comment', sa.UnicodeText(), nullable=True),
    sa.Column('pvep_comment', sa.UnicodeText(), nullable=True),
    sa.Column('overview_comment', sa.UnicodeText(), nullable=True),
    sa.ForeignKeyConstraint(['visit_id'], ['visits.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result_no', sa.Integer(), nullable=False),
    sa.Column('is_average', sa.Boolean(), nullable=True),
    sa.Column('channel_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['step_channel.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('channel_id', 'result_no', name='results_pk')
    )
    op.create_table('step_channel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('step_id', sa.Integer(), nullable=True),
    sa.Column('channel_no', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['step_id'], ['steps.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('step_id', 'channel_no', name='stepchannel_pk')
    )
    op.create_table('steps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.Column('mferg_param_id', sa.Integer(), nullable=True),
    sa.Column('erg_param_id', sa.Integer(), nullable=True),
    sa.Column('vep_param_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['erg_param_id'], ['erg_params.id'], ),
    sa.ForeignKeyConstraint(['mferg_param_id'], ['mferg_params.id'], ),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ),
    sa.ForeignKeyConstraint(['vep_param_id'], ['vep_params.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_date', sa.DateTime(), nullable=False),
    sa.Column('visit_id', sa.Integer(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('protocol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['protocol_id'], ['protocols.id'], ),
    sa.ForeignKeyConstraint(['visit_id'], ['visits.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tests_test_date'), 'tests', ['test_date'], unique=False)
    op.create_table('timeseries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_trial', sa.Boolean(), nullable=False),
    sa.Column('result_id', sa.Integer(), nullable=True),
    sa.Column('start', sa.Integer(), nullable=False),
    sa.Column('interval', sa.Numeric(), nullable=False),
    sa.Column('x_units', sa.Unicode(), nullable=False),
    sa.Column('y_units', sa.Unicode(), nullable=False),
    sa.Column('data_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['data_id'], ['timeseriesdata.id'], ),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('timeseries_timeseriesdata',
    sa.Column('timeseries_id', sa.Integer(), nullable=True),
    sa.Column('timeseriesdata_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['timeseries_id'], ['timeseries.id'], ),
    sa.ForeignKeyConstraint(['timeseriesdata_id'], ['timeseriesdata.id'], )
    )
    op.create_table('timeseriesdata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timeseries_id', sa.Integer(), nullable=True),
    sa.Column('values', sa.ARRAY(sa.Numeric()), nullable=True),
    sa.Column('hash_str', sa.Unicode(), nullable=False),
    sa.ForeignKeyConstraint(['timeseries_id'], ['timeseries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_data_hash', 'timeseriesdata', ['hash_str'], unique=True)
    op.create_table('vep_params',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Unicode(), nullable=True),
    sa.Column('size', sa.Numeric(), nullable=False),
    sa.Column('eye', sa.Enum('left', 'right', 'binocular', 'none', name='vep_eye_tested'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('visit_tests',
    sa.Column('visit_id', sa.Integer(), nullable=True),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ),
    sa.ForeignKeyConstraint(['visit_id'], ['visits.id'], )
    )
    op.create_table('visits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('visit_date', sa.Date(), nullable=False),
    sa.Column('notes', sa.UnicodeText(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('patient_id', 'visit_date', name='pk_visit')
    )
    op.create_index(op.f('ix_visits_visit_date'), 'visits', ['visit_date'], unique=False)
    op.drop_table('sessions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('data', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('expiry', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='sessions_pkey'),
    sa.UniqueConstraint('session_id', name='sessions_session_id_key')
    )
    op.drop_index(op.f('ix_visits_visit_date'), table_name='visits')
    op.drop_table('visits')
    op.drop_table('visit_tests')
    op.drop_table('vep_params')
    op.drop_index('idx_data_hash', table_name='timeseriesdata')
    op.drop_table('timeseriesdata')
    op.drop_table('timeseries_timeseriesdata')
    op.drop_table('timeseries')
    op.drop_index(op.f('ix_tests_test_date'), table_name='tests')
    op.drop_table('tests')
    op.drop_table('steps')
    op.drop_table('step_channel')
    op.drop_table('results')
    op.drop_table('reports')
    op.drop_table('protocols')
    op.drop_table('protocol_steps_vep')
    op.drop_table('protocol_steps_mferg')
    op.drop_table('protocol_steps_erg')
    op.drop_index(op.f('ix_patients_phi_lname'), table_name='patients_phi')
    op.drop_table('patients_phi')
    op.drop_table('patients')
    op.drop_table('patient_diagnoses')
    op.drop_table('mferg_params')
    op.drop_table('markers')
    op.drop_table('erg_params')
    op.drop_index(op.f('ix_doctors_lname'), table_name='doctors')
    op.drop_table('doctors')
    op.drop_index(op.f('ix_diagnoses_name'), table_name='diagnoses')
    op.drop_table('diagnoses')
    # ### end Alembic commands ###
