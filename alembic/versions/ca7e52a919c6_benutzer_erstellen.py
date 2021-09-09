"""Benutzer erstellen

Revision ID: ca7e52a919c6
Revises: 74e60d62286a
Create Date: 2021-08-27 22:12:09.912359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship

# revision identifiers, used by Alembic.
revision = 'ca7e52a919c6'
down_revision = '74e60d62286a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('Benutzer',
    sa.Column('benutzername',sa.String(45), primary_key=True),
    sa.Column('name',sa.String(45), nullable=False),
    sa.Column('emailAdresse',sa.String(45), nullable=False, unique=True),
    sa.Column('passwort',sa.String(45), nullable=False),
    sa.Column('adresseRef',sa.Integer(), sa.ForeignKey('Adresse.Adresse.id'), nullable=False, index=True),
    sa.Column('RolleRef',sa.Integer(), sa.ForeignKey('Rolle.idRolle',), nullable=False, index=True),
    sa.Column('eingeloggt', sa.Boolean(),nullable=False, default=False),
    relationship('Adresse'),
    relationship('Adresse')
    )


def downgrade():
    pass
