"""empty message

Revision ID: e3fa96b88a15
Revises: f114a1bcc4cb
Create Date: 2020-03-29 21:58:50.781081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3fa96b88a15'
down_revision = 'f114a1bcc4cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('referrals_user_id_fkey', 'referrals', type_='foreignkey')
    op.drop_column('referrals', 'user_id')
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('payment_types', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('referral_id', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'referral_id')
    op.drop_column('users', 'payment_types')
    op.drop_column('users', 'created_at')
    op.add_column('referrals', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('referrals_user_id_fkey', 'referrals', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###