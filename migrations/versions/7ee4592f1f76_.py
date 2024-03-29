"""empty message

Revision ID: 7ee4592f1f76
Revises: 5b99d4139b32
Create Date: 2020-06-26 15:49:43.300891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7ee4592f1f76"
down_revision = "5b99d4139b32"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("_hash_esp_id_uc", "probes", ["HASH", "esp_id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("_hash_esp_id_uc", "probes", type_="unique")
    # ### end Alembic commands ###
