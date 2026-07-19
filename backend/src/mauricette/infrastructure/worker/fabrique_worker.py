"""Construction des cas d'usage du worker RAG, en dehors de tout câblage FastAPI.

Les adaptateurs (extraction, découpage, embedding, stockage) sont sans état vis-à-vis
de la base : ils sont construits une seule fois pour toute la durée de vie du worker,
via `construire_adaptateurs`. Les dépôts (repositories), eux, dépendent d'une session
SQLAlchemy et sont reconstruits à chaque tâche traitée, via `construire_gestionnaires_par_type`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from mauricette.application.cas_usage.decouper_document import (
    CommandeDecouperDocument,
    DecouperDocument,
)
from mauricette.application.cas_usage.extraire_document import (
    CommandeExtraireDocument,
    ExtraireDocument,
)
from mauricette.application.cas_usage.regenerer_reponses_appel_offre import (
    CommandeRegenererReponsesAppelOffre,
    RegenererReponsesAppelOffre,
)
from mauricette.application.cas_usage.vectoriser_document import (
    CommandeVectoriserDocument,
    VectoriserDocument,
)
from mauricette.config.parametres import Parametres
from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.ports.decoupeur_document import DecoupeurDocumentPort
from mauricette.domaine.ports.embedding import EmbeddingPort
from mauricette.domaine.ports.extracteur_document import ExtracteurDocumentPort
from mauricette.domaine.ports.generation_reponse import GenerationReponsePort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
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
from mauricette.infrastructure.persistence.postgres.reponse_question_repository_sql import (
    ReponseQuestionRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.tache_traitement_repository_sql import (
    TacheTraitementRepositorySQL,
)
from mauricette.infrastructure.rag.decoupeur_hierarchique import DecoupeurHierarchique
from mauricette.infrastructure.rag.docling_adapter import DoclingAdapter
from mauricette.infrastructure.rag.mistral_embedding_adapter import MistralEmbeddingAdapter
from mauricette.infrastructure.rag.mistral_generation_adapter import MistralGenerationAdapter
from mauricette.infrastructure.stockage.fabrique_stockage import creer_adaptateur_stockage


@dataclass(frozen=True)
class AdaptateursRag:
    """Adaptateurs sans état du pipeline RAG, construits une seule fois par le worker."""

    extracteur: ExtracteurDocumentPort
    decoupeur: DecoupeurDocumentPort
    embedding: EmbeddingPort
    generation: GenerationReponsePort
    stockage: StockageDocumentPort


def construire_adaptateurs(parametres: Parametres) -> AdaptateursRag:
    """Construit les adaptateurs RAG une seule fois pour toute la durée de vie du worker."""
    return AdaptateursRag(
        extracteur=DoclingAdapter(),
        decoupeur=DecoupeurHierarchique(parametres),
        embedding=MistralEmbeddingAdapter(parametres),
        generation=MistralGenerationAdapter(parametres),
        stockage=creer_adaptateur_stockage(parametres),
    )


def construire_gestionnaires_par_type(
    session: Session, adaptateurs: AdaptateursRag, parametres: Parametres
) -> dict[TypeTache, Callable[[UUID], None]]:
    """Construit, pour la session donnée, la fonction à exécuter pour chaque type de tâche."""
    depot_documents = DocumentRepositorySQL(session)
    depot_traitement_rag = DocumentTraitementRagRepositorySQL(session)
    depot_chunks = ChunkRepositorySQL(session)
    depot_taches = TacheTraitementRepositorySQL(session)
    depot_referentiels_ao = ReferentielAppelOffreRepositorySQL(session)
    depot_questions = QuestionReferentielRepositorySQL(session)
    depot_reponses = ReponseQuestionRepositorySQL(session)

    extraire = ExtraireDocument(
        depot_documents,
        depot_traitement_rag,
        depot_taches,
        adaptateurs.stockage,
        adaptateurs.extracteur,
    )
    decouper = DecouperDocument(
        depot_documents,
        depot_traitement_rag,
        depot_chunks,
        depot_taches,
        adaptateurs.stockage,
        adaptateurs.decoupeur,
    )
    vectoriser = VectoriserDocument(
        depot_documents, depot_traitement_rag, depot_chunks, depot_taches, adaptateurs.embedding
    )
    regenerer = RegenererReponsesAppelOffre(
        depot_referentiels_ao,
        depot_questions,
        depot_documents,
        depot_chunks,
        depot_reponses,
        adaptateurs.embedding,
        adaptateurs.generation,
        parametres,
    )

    return {
        TypeTache.EXTRACTION_DOCUMENT: lambda document_id: extraire.executer(
            CommandeExtraireDocument(document_id)
        ),
        TypeTache.DECOUPAGE_DOCUMENT: lambda document_id: decouper.executer(
            CommandeDecouperDocument(document_id)
        ),
        TypeTache.EMBEDDING_DOCUMENT: lambda document_id: vectoriser.executer(
            CommandeVectoriserDocument(document_id)
        ),
        TypeTache.REGENERATION_REPONSES_AO: lambda appel_offre_id: regenerer.executer(
            CommandeRegenererReponsesAppelOffre(appel_offre_id)
        ),
    }
