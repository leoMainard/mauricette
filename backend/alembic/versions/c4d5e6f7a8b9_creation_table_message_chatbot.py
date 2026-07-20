"""creation table message_chatbot

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-07-20 17:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'message_chatbot',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=True),
        sa.Column('score_confiance', sa.Float(), nullable=True),
        sa.Column('citations', JSONB(), nullable=False),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_message_chatbot_appel_offre_id_date_creation',
        'message_chatbot',
        ['appel_offre_id', 'date_creation'],
    )


def downgrade() -> None:
    op.drop_index('ix_message_chatbot_appel_offre_id_date_creation', table_name='message_chatbot')
    op.drop_table('message_chatbot')
