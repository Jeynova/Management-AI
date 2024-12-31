"""Add file_answers table evenement

Revision ID: 8d536713627d
Revises: a06d7cbce6ad
Create Date: 2024-12-30 10:09:26.082494

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8d536713627d'
down_revision = 'a06d7cbce6ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])

    with op.batch_alter_table('file_answers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('evenement_id', sa.Integer(), nullable=False))
        batch_op.drop_constraint('file_answers_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])
        batch_op.drop_column('event_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file_answers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('file_answers_ibfk_1', 'evenements', ['event_id'], ['id'])
        batch_op.drop_column('evenement_id')

    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###