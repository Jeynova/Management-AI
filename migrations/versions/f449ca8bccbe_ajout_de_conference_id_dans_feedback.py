"""Ajout de conference_id dans Feedback

Revision ID: f449ca8bccbe
Revises: ea23aceea936
Create Date: 2024-12-28 22:09:40.694339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f449ca8bccbe'
down_revision = 'ea23aceea936'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('conferences', schema=None) as batch_op:
        batch_op.add_column(sa.Column('conference_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])

    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('conferences', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('conference_id')

    # ### end Alembic commands ###
