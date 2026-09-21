"""add_role_to_users

Revision ID: 7375bf245081
Revises: 49b3700a14eb
Create Date: 2026-09-21 04:50:28.579629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7375bf245081'
down_revision: Union[str, Sequence[str], None] = '49b3700a14eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('role', sa.String(), nullable=True, server_default='patient'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
