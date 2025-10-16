"""chage uid type to text

Revision ID: d20d0cf14c80
Revises: 0e295b6fc265
Create Date: 2025-10-16 09:38:40.172685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd20d0cf14c80'
down_revision: Union[str, Sequence[str], None] = '0e295b6fc265'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('yott_message_s_id_fkey', 'yott_message', type_='foreignkey')
    op.drop_constraint('yott_user_belong_to_chat_uid_fkey', 'yott_user_belong_to_chat', type_='foreignkey')
    
    # Drop the sequence and primary key constraint
    op.drop_constraint('yott_person_pkey', 'yott_person', type_='primary')
    op.execute("DROP SEQUENCE IF EXISTS yott_person_uid_seq CASCADE")
    
    # Change column types from INTEGER to TEXT
    op.alter_column('yott_person', 'uid',
               existing_type=sa.INTEGER(),
               type_=sa.Text(),
               existing_nullable=False)
    
    op.alter_column('yott_message', 's_id',
               existing_type=sa.INTEGER(),
               type_=sa.Text(),
               existing_nullable=True)
               
    op.alter_column('yott_user_belong_to_chat', 'uid',
               existing_type=sa.INTEGER(),
               type_=sa.Text(),
               existing_nullable=True)
    
    # Recreate primary key constraint
    op.create_primary_key('yott_person_pkey', 'yott_person', ['uid'])
    
    # Recreate foreign key constraints
    op.create_foreign_key('yott_message_s_id_fkey', 'yott_message', 'yott_person', ['s_id'], ['uid'])
    op.create_foreign_key('yott_user_belong_to_chat_uid_fkey', 'yott_user_belong_to_chat', 'yott_person', ['uid'], ['uid'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints
    op.drop_constraint('yott_message_s_id_fkey', 'yott_message', type_='foreignkey')
    op.drop_constraint('yott_user_belong_to_chat_uid_fkey', 'yott_user_belong_to_chat', type_='foreignkey')
    op.drop_constraint('yott_person_pkey', 'yott_person', type_='primary')
    
    # Change column types back from TEXT to INTEGER
    op.alter_column('yott_person', 'uid',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    
    op.alter_column('yott_message', 's_id',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               existing_nullable=True)
               
    op.alter_column('yott_user_belong_to_chat', 'uid',
               existing_type=sa.Text(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    
    # Recreate sequence and primary key
    op.execute("CREATE SEQUENCE yott_person_uid_seq")
    op.execute("ALTER TABLE yott_person ALTER COLUMN uid SET DEFAULT nextval('yott_person_uid_seq'::regclass)")
    op.create_primary_key('yott_person_pkey', 'yott_person', ['uid'])
    
    # Recreate foreign key constraints
    op.create_foreign_key('yott_message_s_id_fkey', 'yott_message', 'yott_person', ['s_id'], ['uid'])
    op.create_foreign_key('yott_user_belong_to_chat_uid_fkey', 'yott_user_belong_to_chat', 'yott_person', ['uid'], ['uid'])
