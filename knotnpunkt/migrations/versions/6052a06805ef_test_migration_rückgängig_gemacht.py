"""Test migration rückgängig gemacht

Revision ID: 6052a06805ef
Revises: de08052b9eb2
Create Date: 2022-03-05 19:51:43.253928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6052a06805ef'
down_revision = 'de08052b9eb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test',
    sa.Column('idTest', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('idTest')
    )
    # ### end Alembic commands ###
