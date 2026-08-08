"""feedback_reponse : sources attendues (documents) et types d'erreur en listes

Remplace les colonnes texte libre `source_attendue` (str | None) et
`type_erreur` (une seule valeur) par deux colonnes JSONB liste :
`sources_attendues_ids` (ids de documents déposés) et `types_erreur`
(plusieurs valeurs possibles). Même pattern que `citations` sur
`reponse_question`/`message_chatbot`.

`source_attendue` était du texte libre, non convertible automatiquement en
id de document : la seule ligne existante avec cette valeur ("CCTP") est
perdue au downgrade comme à l'upgrade (décision explicite, cf. plan). Les
valeurs existantes de `type_erreur` sont migrées vers `types_erreur` sous
forme de liste à un élément.

Revision ID: d4e5f6a7b8c1
Revises: c3d4e5f6a7b9
Create Date: 2026-08-09 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c1'
down_revision: Union[str, None] = 'c3d4e5f6a7b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'feedback_reponse',
        sa.Column('sources_attendues_ids', JSONB(), nullable=False, server_default='[]'),
    )
    op.add_column(
        'feedback_reponse',
        sa.Column('types_erreur', JSONB(), nullable=False, server_default='[]'),
    )

    # Migre les types_erreur existants (valeur unique) vers une liste à un élément.
    op.execute(
        """
        UPDATE feedback_reponse
        SET types_erreur = jsonb_build_array(type_erreur)
        WHERE type_erreur IS NOT NULL
        """
    )

    op.drop_column('feedback_reponse', 'source_attendue')
    op.drop_column('feedback_reponse', 'type_erreur')

    op.alter_column('feedback_reponse', 'sources_attendues_ids', server_default=None)
    op.alter_column('feedback_reponse', 'types_erreur', server_default=None)


def downgrade() -> None:
    op.add_column('feedback_reponse', sa.Column('source_attendue', sa.Text(), nullable=True))
    op.add_column('feedback_reponse', sa.Column('type_erreur', sa.String(30), nullable=True))

    # Reprend uniquement le premier type d'erreur de la liste ; les sources
    # (désormais des ids de documents, plus du texte libre) ne sont pas reconverties.
    op.execute(
        """
        UPDATE feedback_reponse
        SET type_erreur = types_erreur ->> 0
        WHERE jsonb_array_length(types_erreur) > 0
        """
    )

    op.drop_column('feedback_reponse', 'sources_attendues_ids')
    op.drop_column('feedback_reponse', 'types_erreur')
