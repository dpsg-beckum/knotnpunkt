"""Lager entfernen

Revision ID: f57f6b23f98e
Revises: bd6a7304874b
Create Date: 2021-12-11 21:36:56.004940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f57f6b23f98e'
down_revision = 'bd6a7304874b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('Lager')


def downgrade():
    pass
