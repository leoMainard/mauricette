"""creation tables feedback_general et feedback_reponse

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-07-20 18:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'feedback_general',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('avis', sa.String(length=20), nullable=True),
        sa.Column('commentaire', sa.Text(), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appel_offre_id'),
    )

    op.create_table(
        'feedback_reponse',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('question_referentiel_id', sa.UUID(), nullable=False),
        sa.Column('avis', sa.String(length=20), nullable=True),
        sa.Column('contenu_reponse_snapshot', sa.Text(), nullable=True),
        sa.Column('commentaire', sa.Text(), nullable=True),
        sa.Column('source_attendue', sa.Text(), nullable=True),
        sa.Column('citation_attendue', sa.Text(), nullable=True),
        sa.Column('type_erreur', sa.String(length=30), nullable=True),
        sa.Column('details_erreur', sa.Text(), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_referentiel_id'], ['question_referentiel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appel_offre_id', 'question_referentiel_id'),
    )


def downgrade() -> None:
    op.drop_table('feedback_reponse')
    op.drop_table('feedback_general')
