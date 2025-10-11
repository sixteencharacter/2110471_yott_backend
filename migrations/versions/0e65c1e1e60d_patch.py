"""patch

Revision ID: 0e65c1e1e60d
Revises: 1a41cafa350f
Create Date: 2025-10-12 01:01:55.229519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e65c1e1e60d'
down_revision: Union[str, Sequence[str], None] = '1a41cafa350f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
