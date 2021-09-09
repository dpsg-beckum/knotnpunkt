"""restliche tabellen erstellen

Revision ID: 74e60d62286a
Revises: cc86d7735a89
Create Date: 2021-08-27 15:07:40.647223

"""
import abc
from re import T
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DATETIME, Boolean, String


# revision identifiers, used by Alembic.
revision = '74e60d62286a'
down_revision = 'cc86d7735a89'
branch_labels = None
depends_on = None


def upgrade():
    
    op.create_table("Adresse",
    sa.Column('idAdresse', sa.Integer, primary_key=True),
    sa.Column('strasse', sa.String(45), nullable=False),
    sa.Column('hausnummer',sa.String(10)),
    sa.Column('postleitzahl',sa.String(7)),
    sa.Column('ort',sa.String(45))
    )
    
    op.create_table("Kategorie",
    sa.Column('idKategorie',sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(45), nullable=False),
    sa.Column('istZaehlbar',sa.Boolean(), nullable=False)
    )
    op.create_table("Label",
    sa.Column('idLabel',sa.Integer, primary_key=True),
    sa.Column('name',sa.String(45), nullable=False),
    sa.Column('datentyp',sa.String(45), nullable=False)
    )
    op.create_table("Standarteigenschaft",
    sa.Column('Kategorie_idKategorie',sa.Integer(),sa.ForeignKey('Kategorie.idKategorie'), primary_key=True, nullable=False, index=True),
    sa.Column('Label_idLabel',sa.Integer(),sa.ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True),
    sa.Column('wertInt',sa.String(45)),
    sa.Column('wertString',sa.String(45)),
    sa.Column('wertBool',sa.String(45)),
    relationship('Kategorie'),
    relationship('Label')
    )
    op.create_table("Aktion",
    sa.Column('idAktion',sa.Integer, primary_key=True),
    sa.Column('name',sa.String(45), nullable=False),
    sa.Column('beginn',sa.DATETIME(), nullable=False),
    sa.Column('ende',sa.DATETIME(), nullable=False),
    sa.Column('ansprechpartnerRef',sa.Integer(),sa.ForeignKey('Benutzer.benutzername'), nullable=False, index=True),
    sa.Column('Adresse_idAdresse',sa.Integer(),sa.ForeignKey('Adresse.idAdresse'), nullable=False, index=True),
    relationship('Adresse'),
    relationship('Benutzer')
    )
    op.create_table("Lager",
    sa.Column('idLager',sa.Integer, primary_key=True),
    sa.Column('adresseRef',sa.Integer(),sa.ForeignKey('Adresse.idAdresse'), nullable=False, index=True),
    sa.Column('ansprechpartnerRef',sa.Integer(),sa.ForeignKey('Benutzer.benutzername'), nullable=False, index=True),
    relationship('Adresse'),
    relationship('Benutzer')
    )

    op.create_table("Material",
    sa.Column('idMaterial', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(45), nullable=False),
    sa.Column('Kategorie_idKategorie',sa.Integer(), sa.ForeignKey('Kategorie.idKategorie'), nullable=False, index=True),
    sa.Column('Lager_idLager',sa.Integer(), sa.ForeignKey('Lager.idLager'), nullable=False, index=True),
    relationship('Kategorie'),
    relationship('Lager')

    )
    op.create_table("Eigenschaft",
    sa.Column('Material_idMaterial',sa.Integer(),sa.ForeignKey('Material.idMaterial'), primary_key=True, nullable=False, index=True),
    sa.Column('Label_idLabel',sa.Integer(),sa.ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True),
    sa.Column('wertInt',sa.String(45)),
    sa.Column('wertString',sa.String(45)),
    sa.Column('wertBool',sa.String(45)),
    relationship('Label'),
    relationship('Material')
    )


def downgrade():
    pass
