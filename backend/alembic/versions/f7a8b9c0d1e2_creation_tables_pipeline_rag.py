"""creation tables document_traitement_rag chunk tache_traitement

Revision ID: f7a8b9c0d1e2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-19 18:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'f7a8b9c0d1e2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_traitement_rag',
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('extraction_statut', sa.String(length=20), nullable=False),
        sa.Column('extraction_message_erreur', sa.Text(), nullable=True),
        sa.Column('extraction_date_maj', sa.DateTime(timezone=True), nullable=True),
        sa.Column('decoupage_statut', sa.String(length=20), nullable=False),
        sa.Column('decoupage_message_erreur', sa.Text(), nullable=True),
        sa.Column('decoupage_date_maj', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding_statut', sa.String(length=20), nullable=False),
        sa.Column('embedding_message_erreur', sa.Text(), nullable=True),
        sa.Column('embedding_date_maj', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['document.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('document_id'),
    )

    op.create_table(
        'chunk',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('appel_offre_id', sa.UUID(), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=False),
        sa.Column('type_chunk', sa.String(length=20), nullable=False),
        sa.Column('page_debut', sa.Integer(), nullable=True),
        sa.Column('page_fin', sa.Integer(), nullable=True),
        sa.Column('titre_section', sa.String(length=1000), nullable=True),
        sa.Column('ordre', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['document.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appel_offre_id'], ['appel_offre.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chunk_appel_offre_id', 'chunk', ['appel_offre_id'])
    op.create_index(
        'ix_chunk_embedding_hnsw',
        'chunk',
        ['embedding'],
        postgresql_using='hnsw',
        postgresql_ops={'embedding': 'vector_cosine_ops'},
    )

    op.create_table(
        'tache_traitement',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('type_tache', sa.String(length=50), nullable=False),
        sa.Column('reference_id', sa.UUID(), nullable=False),
        sa.Column('statut', sa.String(length=20), nullable=False),
        sa.Column('tentatives', sa.Integer(), nullable=False),
        sa.Column('message_erreur', sa.Text(), nullable=True),
        sa.Column('date_prochaine_tentative', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_reservation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_maj', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_tache_traitement_statut_type_date',
        'tache_traitement',
        ['statut', 'type_tache', 'date_creation'],
    )


def downgrade() -> None:
    op.drop_table('tache_traitement')
    op.drop_index('ix_chunk_embedding_hnsw', table_name='chunk')
    op.drop_index('ix_chunk_appel_offre_id', table_name='chunk')
    op.drop_table('chunk')
    op.drop_table('document_traitement_rag')
