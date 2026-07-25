"""creation table groupe_utilisateur

Revision ID: a1b2c3d4e5f7
Revises: d5e6f7a8b9c0
Create Date: 2026-07-25 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'groupe_utilisateur',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('groupe_utilisateur')
