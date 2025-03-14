"""adding link categories and other ai data

Revision ID: 18e694518611
Revises: e0b3146f8655
Create Date: 2025-03-01 12:28:21.971493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '18e694518611'
down_revision: Union[str, None] = 'e0b3146f8655'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Create category table
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=False)
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=False)
    op.create_index(op.f('ix_category_user_id'), 'category', ['user_id'], unique=False)
    
    # Add new columns to link table
    op.add_column('link', sa.Column('original_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('link', sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('link', sa.Column('short_summary', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    
    # Create and add enum columns
    content_type_enum = postgresql.ENUM("WEBPAGE", "YOUTUBE", "SPOTIFY", "TWITTER", "GITHUB", "PDF", "UNKNOWN", name="contenttype")
    content_type_enum.create(op.get_bind())
    op.add_column(
        "link", sa.Column("content_type", content_type_enum, nullable=True)
    )
    
    op.add_column('link', sa.Column('author', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('link', sa.Column('duration', sa.Integer(), nullable=True))
    op.add_column('link', sa.Column('thumbnail_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('link', sa.Column('raw_metadata', sa.JSON(), nullable=True))
    
    processing_status_enum = postgresql.ENUM("PENDING", "PROCESSING", "COMPLETE", "ERROR", name="processingstatus")
    processing_status_enum.create(op.get_bind())
    op.add_column(
        "link", sa.Column("processing_status", processing_status_enum, nullable=True)
    )
    
    op.add_column('link', sa.Column('processing_error', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    
    # Add new timestamp columns but don't drop the old one yet
    op.add_column('link', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('link', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('link', sa.Column('processed_at', sa.DateTime(), nullable=True))
    
    # Copy existing timestamp values
    op.execute('UPDATE link SET created_at = timestamp, updated_at = timestamp')
    
    # Now make timestamps non-nullable
    op.alter_column('link', 'created_at', nullable=False)
    op.alter_column('link', 'updated_at', nullable=False)
    
    # Set default values for new enum columns
    op.execute("UPDATE link SET content_type = 'UNKNOWN' WHERE content_type IS NULL")
    op.execute("UPDATE link SET processing_status = 'COMPLETE' WHERE processing_status IS NULL")
    
    # Handle user_id foreign key
    # First, we need to handle any links without user_ids
    # You may want to adjust this based on your needs:
    # Option 1: Delete orphaned links
    op.execute('DELETE FROM link WHERE user_id IS NULL')
    # Option 2: Assign to a default user (uncomment if needed)
    # op.execute('UPDATE link SET user_id = 1 WHERE user_id IS NULL')
    
    # Now we can safely make user_id non-nullable
    op.alter_column('link', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    
    # Add category relationship
    op.add_column('link', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_link_category_id'), 'link', ['category_id'], unique=False)
    op.create_index(op.f('ix_link_user_id'), 'link', ['user_id'], unique=False)
    op.create_foreign_key(None, 'link', 'category', ['category_id'], ['id'])
    
    # Finally drop the old timestamp column
    op.drop_column('link', 'timestamp')
    
    # Add user preferences with defaults
    op.add_column('user', sa.Column('allow_ai_categorization', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('user', sa.Column('allow_ai_create_categories', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('user', sa.Column('ai_confidence_threshold', sa.Float(), server_default='0.8', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'ai_confidence_threshold')
    op.drop_column('user', 'allow_ai_create_categories')
    op.drop_column('user', 'allow_ai_categorization')
    
    # Restore timestamp column and copy data back
    op.add_column('link', sa.Column('timestamp', postgresql.TIMESTAMP(), nullable=True))
    op.execute('UPDATE link SET timestamp = created_at')
    op.alter_column('link', 'timestamp', nullable=False)
    
    op.drop_constraint(None, 'link', type_='foreignkey')
    op.drop_index(op.f('ix_link_user_id'), table_name='link')
    op.drop_index(op.f('ix_link_category_id'), table_name='link')
    op.alter_column('link', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('link', 'category_id')
    op.drop_column('link', 'processed_at')
    op.drop_column('link', 'updated_at')
    op.drop_column('link', 'created_at')
    op.drop_column('link', 'processing_error')
    op.drop_column('link', 'processing_status')
    processing_status_enum = postgresql.ENUM("PENDING", "PROCESSING", "COMPLETE", "ERROR", name="processingstatus")
    processing_status_enum.drop(op.get_bind())
    op.drop_column('link', 'raw_metadata')
    op.drop_column('link', 'thumbnail_url')
    op.drop_column('link', 'duration')
    op.drop_column('link', 'author')
    op.drop_column('link', 'content_type')
    content_type_enum = postgresql.ENUM("WEBPAGE", "YOUTUBE", "SPOTIFY", "TWITTER", "GITHUB", "PDF", "UNKNOWN", name="contenttype")
    content_type_enum.drop(op.get_bind())
    op.drop_column('link', 'short_summary')
    op.drop_column('link', 'title')
    op.drop_column('link', 'original_url')
    op.drop_index(op.f('ix_category_user_id'), table_name='category')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.drop_table('category')
    # ### end Alembic commands ###
