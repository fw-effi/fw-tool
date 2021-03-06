"""empty message

Revision ID: 644e7314f591
Revises: 
Create Date: 2019-11-05 13:04:50.900816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '644e7314f591'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Firefighter', schema=None) as batch_op:
        batch_op.create_unique_constraint('firefighter_uid_unique_constraint', ['uid'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Firefighter', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
