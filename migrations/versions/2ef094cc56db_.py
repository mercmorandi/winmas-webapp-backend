"""empty message

Revision ID: 2ef094cc56db
Revises: 200edd3062cc
Create Date: 2020-06-05 16:57:52.643491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ef094cc56db"
down_revision = "200edd3062cc"
branch_labels = None
depends_on = None

OLD_STATUS = sa.Enum("unchecked", "tracked", "discarded", name="probe_status")
NEW_STATUS = sa.Enum(
    "unchecked", "pending", "tracked", "discarded", name="probe_status"
)


def upgrade():
    op.execute("alter type probe_status rename to probe_status_old")
    old_type = OLD_STATUS.copy()
    old_type.name = "probe_status_old"
    NEW_STATUS.create(op.get_bind())
    op.alter_column(
        "probes",
        "probe_status",
        existing_type=old_type,
        type_=NEW_STATUS,
        postgresql_using="probe_status::text::probe_status",
    )
    old_type.drop(op.get_bind())


def downgrade():
    op.execute("alter type probe_status rename to probe_status_old")
    old_type = NEW_STATUS.copy()
    old_type.name = "probe_status_old"
    OLD_STATUS.create(op.get_bind())
    op.alter_column(
        "probes",
        "probe_status",
        existing_type=old_type,
        type_=OLD_STATUS,
        postgresql_using="probe_status::text::probe_status",
    )
    old_type.drop(op.get_bind())
