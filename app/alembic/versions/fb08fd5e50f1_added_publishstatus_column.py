"""Added PublishStatus column

Revision ID: fb08fd5e50f1
Revises: 
Create Date: 2025-02-14 10:32:52.073684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fb08fd5e50f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('seotable')
    op.add_column('blogtable', sa.Column('PublishStatus', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('blogtable', 'PublishStatus')
    op.create_table('seotable',
    sa.Column('SEOId', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('meta_description', mysql.VARCHAR(collation='utf8mb4_bin', length=255), nullable=True),
    sa.Column('meta_keywords', mysql.VARCHAR(collation='utf8mb4_bin', length=255), nullable=True),
    sa.Column('meta_author', mysql.VARCHAR(collation='utf8mb4_bin', length=255), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('BlogId', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['BlogId'], ['blogtable.BlogId'], name='seotable_ibfk_1'),
    sa.PrimaryKeyConstraint('SEOId'),
    mysql_collate='utf8mb4_bin',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_seotable_SEOId', 'seotable', ['SEOId'], unique=False)
    # ### end Alembic commands ###
