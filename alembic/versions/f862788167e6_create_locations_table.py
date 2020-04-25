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

def downgrade():
    op.drop_table("locations")

def upgrade():
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("HASH", sa.String(length=255), nullable=False),
        sa.Column("SSID", sa.String(length=255), nullable=False),
        sa.Column("insertion_date", sa.DateTime(), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("MAC_id", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"))

    op.create_foreign_key(
        'fk_locations_MAC_devices',
        'locations', 'devices',
        ['MAC_id'], ['MAC'],
    )