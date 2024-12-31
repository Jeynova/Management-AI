"""Add file_answers table

Revision ID: a06d7cbce6ad
Revises: 003710c65e2e
Create Date: 2024-12-30 10:08:18.459056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a06d7cbce6ad'
down_revision = '003710c65e2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('response', sa.Text(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['evenements.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB',
    mysql_row_format='DYNAMIC'
    )
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'conferences', ['conference_id'], ['id'])
        batch_op.create_foreign_key(None, 'evenements', ['evenement_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    op.drop_table('file_answers')
    # ### end Alembic commands ###
