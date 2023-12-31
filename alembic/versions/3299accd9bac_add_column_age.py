"""add column age

Revision ID: 3299accd9bac
Revises: 9b805a2ec3d5
Create Date: 2023-07-28 16:43:28.465054

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '3299accd9bac'
down_revision = '9b805a2ec3d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usertable', sa.Column('Typeofuser', sqlalchemy_utils.types.choice.ChoiceType(choices=(('0', 'admin'), ('1', 'editer'), ('2', 'NULL'))), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usertable', 'Typeofuser')
    # ### end Alembic commands ###
