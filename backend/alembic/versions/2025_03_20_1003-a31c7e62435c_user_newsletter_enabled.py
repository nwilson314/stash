"""user newsletter enabled

Revision ID: a31c7e62435c
Revises: 18e694518611
Create Date: 2025-03-20 10:03:55.151056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a31c7e62435c'
down_revision: Union[str, None] = '18e694518611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('link', 'processing_status',
               existing_type=postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETE', 'ERROR', name='processingstatus'),
               nullable=False)
    op.add_column('user', sa.Column('newsletter_enabled', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('newsletter_frequency', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.execute('UPDATE "user" SET newsletter_enabled = false WHERE newsletter_enabled IS NULL')
    op.execute('UPDATE "user" SET newsletter_frequency = \'weekly\' WHERE newsletter_frequency IS NULL')
    op.alter_column('user', 'newsletter_enabled', nullable=False)
    op.alter_column('user', 'newsletter_frequency', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'newsletter_frequency')
    op.drop_column('user', 'newsletter_enabled')
    op.alter_column('link', 'processing_status',
               existing_type=postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETE', 'ERROR', name='processingstatus'),
               nullable=True)
    # ### end Alembic commands ###
