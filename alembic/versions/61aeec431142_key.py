"""key

Revision ID: 61aeec431142
Revises: 03838bf25b55
Create Date: 2023-07-28 17:12:24.789214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61aeec431142'
down_revision = '03838bf25b55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blogtable', sa.Column('admin_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'blogtable', 'Admintable', ['admin_id'], ['UserId'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'blogtable', type_='foreignkey')
    op.drop_column('blogtable', 'admin_id')
    # ### end Alembic commands ###
