"""Suppression cascade orphan

Revision ID: 29812110b569
Revises: c8436355d5df
Create Date: 2024-12-28 19:39:58.932607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29812110b569'
down_revision = 'c8436355d5df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
