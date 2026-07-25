"""creation table utilisateur

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-07-25 09:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'utilisateur',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('mot_de_passe_hash', sa.String(length=255), nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('statut', sa.String(length=50), nullable=False),
        sa.Column('groupe_id', sa.UUID(), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['groupe_id'], ['groupe_utilisateur.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_utilisateur_email', 'utilisateur', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_utilisateur_email', table_name='utilisateur')
    op.drop_table('utilisateur')
