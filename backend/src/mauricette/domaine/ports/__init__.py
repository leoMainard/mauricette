"""Ports (interfaces) du domaine, à implémenter par la couche infrastructure."""

from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.decoupeur_document import DecoupeurDocumentPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.embedding import EmbeddingPort
from mauricette.domaine.ports.extracteur_document import ExtracteurDocumentPort
from mauricette.domaine.ports.generation_reponse import GenerationReponsePort
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.domaine.ports.reponse_question_repository import (
    ReponseQuestionRepositoryPort,
)
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort

__all__ = [
    "AppelOffreRepositoryPort",
    "ChunkRepositoryPort",
    "DecoupeurDocumentPort",
    "DocumentRepositoryPort",
    "DocumentTraitementRagRepositoryPort",
    "EmbeddingPort",
    "ExtracteurDocumentPort",
    "GenerationReponsePort",
    "QuestionReferentielRepositoryPort",
    "ReferentielAppelOffreRepositoryPort",
    "ReferentielRepositoryPort",
    "ReponseQuestionRepositoryPort",
    "SectionReferentielRepositoryPort",
    "StockageDocumentPort",
    "TacheTraitementRepositoryPort",
]
