"""empty message

Revision ID: fb231bfe9776
Revises: 7ee4592f1f76
Create Date: 2020-06-30 16:23:44.198814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb231bfe9776'
down_revision = '7ee4592f1f76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('probes', sa.Column('seqnum', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('probes', 'seqnum')
    # ### end Alembic commands ###
