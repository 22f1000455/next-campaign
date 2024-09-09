"""Update backref names to resolve conflict

Revision ID: fe5f12f68ab0
Revises: c9383b883de0
Create Date: 2024-08-10 08:54:16.622954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe5f12f68ab0'
down_revision = 'c9383b883de0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('influencer_profile', schema=None) as batch_op:
        batch_op.alter_column('niche',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('reach',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('influencer_profile', schema=None) as batch_op:
        batch_op.alter_column('reach',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('niche',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)

    # ### end Alembic commands ###
