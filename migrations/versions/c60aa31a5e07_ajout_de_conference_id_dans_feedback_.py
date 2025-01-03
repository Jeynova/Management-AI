"""Ajout de conference_id dans Feedback suppression dans conference 2

Revision ID: c60aa31a5e07
Revises: cd34eb7c2acf
Create Date: 2024-12-28 22:17:27.369197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c60aa31a5e07'
down_revision = 'cd34eb7c2acf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
