"""user timestamps

Revision ID: ef4cdd57d5e1
Revises: a31c7e62435c
Create Date: 2025-04-01 09:56:36.677743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ef4cdd57d5e1'
down_revision: Union[str, None] = 'a31c7e62435c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("NOW()")))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text("NOW()")))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    # ### end Alembic commands ###
