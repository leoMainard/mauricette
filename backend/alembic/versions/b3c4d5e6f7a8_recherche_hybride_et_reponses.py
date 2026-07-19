"""ajout recherche plein texte sur chunk et table reponse_question

Revision ID: b3c4d5e6f7a8
Revises: f7a8b9c0d1e2
Create Date: 2026-07-19 23:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'f7a8b9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chunk',
        sa.Column(
            'contenu_tsv',
            TSVECTOR(),
            sa.Computed("to_tsvector('french', contenu)", persisted=True),
            nullable=True,
        ),
    )
    op.create_index('ix_chunk_contenu_tsv', 'chunk', ['contenu_tsv'], postgresql_using='gin')

    op.create_table(
        'reponse_question',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('question_referentiel_id', sa.UUID(), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=True),
        sa.Column('score_confiance', sa.Float(), nullable=True),
        sa.Column('statut', sa.String(length=30), nullable=False),
        sa.Column('citations', JSONB(), nullable=False),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_referentiel_id'], ['question_referentiel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appel_offre_id', 'question_referentiel_id'),
    )


def downgrade() -> None:
    op.drop_table('reponse_question')
    op.drop_index('ix_chunk_contenu_tsv', table_name='chunk')
    op.drop_column('chunk', 'contenu_tsv')
