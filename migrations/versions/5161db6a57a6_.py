"""empty message

Revision ID: 5161db6a57a6
Revises: 644e7314f591
Create Date: 2020-01-13 20:56:57.824858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5161db6a57a6'
down_revision = '644e7314f591'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Firefighter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('grad_sort', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Firefighter', schema=None) as batch_op:
        batch_op.drop_column('grad_sort')

    # ### end Alembic commands ###
