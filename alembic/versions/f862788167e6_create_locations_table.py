"""create locations table

Revision ID: f862788167e6
Revises: 9205f4f727eb
Create Date: 2020-04-11 18:33:11.667410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f862788167e6'
down_revision = '9205f4f727eb'
branch_labels = None
depends_on = None


def upgrade():
    schema_upgrades()


def downgrade():
    schema_downgrades()

def schema_upgrades():
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("HASH", sa.String(length=255), nullable=False),
        sa.Column("SSID", sa.String(length=255), nullable=False),
        sa.Column("insertion_date", sa.DateTime(), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("MAC_id", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ("MAC_id",), ["devices.MAC"], name="fk_locations_MAC_id_devices"
    )

def schema_downgrades():
    op.drop_table("locations")