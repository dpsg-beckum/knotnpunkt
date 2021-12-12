"""Lagerreferenz entfernen

Revision ID: 1a43cd32167a
Revises: f57f6b23f98e
Create Date: 2021-12-11 22:43:49.424524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a43cd32167a'
down_revision = 'f57f6b23f98e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("Material", "Lager_idLager")


def downgrade():
    pass
