"""empty message

Revision ID: 969a6fdff48a
Revises: 
Create Date: 2020-05-05 21:56:12.613815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '969a6fdff48a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('occurrences', sa.Integer(), nullable=False),
    sa.Column('MAC', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id', 'MAC'),
    sa.UniqueConstraint('MAC')
    )
    op.create_index(op.f('ix_devices_last_update'), 'devices', ['last_update'], unique=False)
    op.create_table('locations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('HASH', sa.String(length=255), nullable=False),
    sa.Column('SSID', sa.String(length=255), nullable=False),
    sa.Column('insertion_date', sa.DateTime(), nullable=False),
    sa.Column('x', sa.Integer(), nullable=False),
    sa.Column('y', sa.Integer(), nullable=False),
    sa.Column('MAC_id', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('probes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=False),
    sa.Column('destination', sa.String(length=255), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('bssid', sa.String(length=255), nullable=False),
    sa.Column('ssid', sa.String(length=255), nullable=False),
    sa.Column('signal_strength_wroom', sa.Integer(), nullable=False),
    sa.Column('signal_strength_rt', sa.Integer(), nullable=False),
    sa.Column('HASH', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('probes')
    op.drop_table('locations')
    op.drop_index(op.f('ix_devices_last_update'), table_name='devices')
    op.drop_table('devices')
    # ### end Alembic commands ###