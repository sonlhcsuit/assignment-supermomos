"""Seeding if data is not available

Revision ID: e72f9c4b85da
Revises: 4e5294d42d67
Create Date: 2025-07-18 20:03:15.947364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from scripts.seeding import seeding_data


# revision identifiers, used by Alembic.
revision: str = 'e72f9c4b85da'
down_revision: Union[str, None] = '4e5294d42d67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    seeding_data(Session(op.get_bind()))


def downgrade() -> None:
    """Downgrade schema."""
    pass
