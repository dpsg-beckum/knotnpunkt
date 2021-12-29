"""Apps hinzufuegen

Revision ID: bd6a7304874b
Revises: ca7e52a919c6
Create Date: 2021-11-19 10:53:26.615602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd6a7304874b'
down_revision = 'ca7e52a919c6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("Apps",
    sa.Column('name', sa.String(45), primary_key=True),
    sa.Column('anzeigename', sa.String(45), nullable=False),
    sa.Column('beschreibung',sa.String(256), nullable=False)
    )

def downgrade():
    pass
