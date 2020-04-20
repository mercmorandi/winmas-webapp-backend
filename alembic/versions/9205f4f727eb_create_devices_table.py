"""create devices table

Revision ID: 9205f4f727eb
Revises: 
Create Date: 2020-04-11 18:33:09.792705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9205f4f727eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    schema_upgrades()


def downgrade():
    schema_downgrades()

def schema_upgrades():
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_update", sa.DateTime(), nullable=False),
        sa.Column("occurrences", sa.Integer(), nullable=False),
        sa.Column("MAC", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

def schema_downgrades():
    op.drop_table("devices")