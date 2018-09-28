"""update results add result trace

Revision ID: ad590527782a
Revises: 377321ac58ec
Create Date: 2018-04-27 16:33:42.649564

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ad590527782a'
down_revision = '377321ac58ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    op.add_column('results', sa.Column('is_average', sa.Boolean(), nullable=True))
    op.add_column('timeseries', sa.Column('is_trial', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('timeseries', 'is_trial')
    op.drop_column('results', 'is_average')
    op.create_table('sessions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('session_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('data', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('expiry', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='sessions_pkey'),
    sa.UniqueConstraint('session_id', name='sessions_session_id_key')
    )
    # ### end Alembic commands ###