"""empty message

Revision ID: 5085e58cc331
Revises: 2ef094cc56db
Create Date: 2020-06-10 16:36:45.618322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5085e58cc331"
down_revision = "2ef094cc56db"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "probes", "timestamp", existing_type=sa.Integer(), type_=sa.BigInteger()
    )


def downgrade():
    op.alter_column(
        "probes", "timestamp", existing_type=sa.BigInteger(), type_=sa.Integer()
    )
