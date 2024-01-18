"""Added account table

Revision ID: d976a2beb686
Revises: 3a2bcc686083
Create Date: 2024-01-05 15:57:43.494969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd976a2beb686'
down_revision = '3a2bcc686083'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usertable', sa.Column('UserAvatar', sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, 'usertable', ['UserAvatar'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'usertable', type_='unique')
    op.drop_column('usertable', 'UserAvatar')
    # ### end Alembic commands ###