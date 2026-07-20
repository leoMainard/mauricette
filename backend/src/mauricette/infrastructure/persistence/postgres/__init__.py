"""Adaptateurs de persistance PostgreSQL (SQLAlchemy)."""

from mauricette.infrastructure.persistence.postgres.appel_offre_repository_sql import (
    AppelOffreRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.base import Base, GestionnaireSessions
from mauricette.infrastructure.persistence.postgres.chunk_repository_sql import ChunkRepositorySQL
from mauricette.infrastructure.persistence.postgres.document_repository_sql import (
    DocumentRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.document_traitement_rag_repository_sql import (
    DocumentTraitementRagRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.question_referentiel_repository_sql import (
    QuestionReferentielRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.referentiel_appel_offre_repository_sql import (
    ReferentielAppelOffreRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.referentiel_repository_sql import (
    ReferentielRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.reponse_question_repository_sql import (
    ReponseQuestionRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.section_referentiel_repository_sql import (
    SectionReferentielRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.tache_traitement_repository_sql import (
    TacheTraitementRepositorySQL,
)

__all__ = [
    "AppelOffreRepositorySQL",
    "Base",
    "ChunkRepositorySQL",
    "DocumentRepositorySQL",
    "DocumentTraitementRagRepositorySQL",
    "GestionnaireSessions",
    "QuestionReferentielRepositorySQL",
    "ReferentielAppelOffreRepositorySQL",
    "ReferentielRepositorySQL",
    "ReponseQuestionRepositorySQL",
    "SectionReferentielRepositorySQL",
    "TacheTraitementRepositorySQL",
]
