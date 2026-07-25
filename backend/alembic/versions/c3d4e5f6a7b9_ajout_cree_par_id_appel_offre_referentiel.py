"""ajout cree_par_id sur appel_offre et referentiel

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-07-25 09:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b9'
down_revision: Union[str, None] = 'b2c3d4e5f6a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('appel_offre', sa.Column('cree_par_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_appel_offre_cree_par_id_utilisateur',
        'appel_offre', 'utilisateur',
        ['cree_par_id'], ['id'],
        ondelete='SET NULL',
    )
    op.add_column('referentiel', sa.Column('cree_par_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_referentiel_cree_par_id_utilisateur',
        'referentiel', 'utilisateur',
        ['cree_par_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_referentiel_cree_par_id_utilisateur', 'referentiel', type_='foreignkey')
    op.drop_column('referentiel', 'cree_par_id')
    op.drop_constraint('fk_appel_offre_cree_par_id_utilisateur', 'appel_offre', type_='foreignkey')
    op.drop_column('appel_offre', 'cree_par_id')
