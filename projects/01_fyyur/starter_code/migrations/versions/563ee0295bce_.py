"""empty message

Revision ID: 563ee0295bce
Revises: fc2e640b430d
Create Date: 2022-08-16 14:06:22.861785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563ee0295bce'
down_revision = 'fc2e640b430d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'seeking',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    op.alter_column('venues', 'seeking',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'seeking',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('artists', 'seeking',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    # ### end Alembic commands ###
