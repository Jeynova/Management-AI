"""Theme evenement

Revision ID: a1f74de332d9
Revises: c60aa31a5e07
Create Date: 2024-12-28 23:25:48.492906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1f74de332d9'
down_revision = 'c60aa31a5e07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
