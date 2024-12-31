"""Ajout de conference_id dans Feedback suppression dans conference

Revision ID: cd34eb7c2acf
Revises: f449ca8bccbe
Create Date: 2024-12-28 22:13:41.019971

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cd34eb7c2acf'
down_revision = 'f449ca8bccbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conferences', schema=None) as batch_op:
        batch_op.drop_constraint('conferences_ibfk_3', type_='foreignkey')
        batch_op.drop_column('conference_id')

    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('conference_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('conference_id')

    with op.batch_alter_table('conferences', schema=None) as batch_op:
        batch_op.add_column(sa.Column('conference_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('conferences_ibfk_3', 'conferences', ['conference_id'], ['id'])

    # ### end Alembic commands ###