"""Rollen-Entität erstellen

Revision ID: cc86d7735a89
Revises: 
Create Date: 2021-08-27 14:28:54.641734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc86d7735a89'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "Rolle",
        sa.Column("idRolle", sa.Integer, primary_key=True),
        sa.Column('name', sa.String(45), nullable=False, unique=True),
        sa.Column('schreibenKalender', sa.Boolean(), default=False),
        sa.Column('lesenKalender', sa.Boolean(), default=False),
        sa.Column('schreibenBenutzer', sa.Boolean(), default=False),
        sa.Column('lesenBenutzer', sa.Boolean(), default=False),
        sa.Column('schreibenMaterial', sa.Boolean(), default=False),
        sa.Column('lesenMaterial', sa.Boolean(), default=False),
        sa.Column('schreibenEinstellungen', sa.Boolean(), default=False),
        sa.Column('lesenEinstellungen', sa.Boolean(), default=False)
    )


def downgrade():
    pass
