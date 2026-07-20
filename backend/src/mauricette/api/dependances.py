"""Câblage des dépendances FastAPI (injection de dépendances).

C'est le seul endroit de la couche `api` qui connaît les implémentations
concrètes (SQLAlchemy, S3/local). Les routes ne dépendent que des cas d'usage,
eux-mêmes définis uniquement en fonction des ports du domaine.
"""

from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from mauricette.application.cas_usage.attacher_referentiel_appel_offre import (
    AttacherReferentielAAppelOffre,
)
from mauricette.application.cas_usage.changer_activation_question_referentiel import (
    ChangerActivationQuestionReferentiel,
)
from mauricette.application.cas_usage.creer_appel_offre import CreerAppelOffre
from mauricette.application.cas_usage.creer_question_referentiel import CreerQuestionReferentiel
from mauricette.application.cas_usage.creer_referentiel import CreerReferentiel
from mauricette.application.cas_usage.creer_section_referentiel import CreerSectionReferentiel
from mauricette.application.cas_usage.deposer_document import DeposerDocument
from mauricette.application.cas_usage.deposer_fichier import DeposerFichier
from mauricette.application.cas_usage.detacher_referentiel_appel_offre import (
    DetacherReferentielDeAppelOffre,
)
from mauricette.application.cas_usage.lister_appels_offre import ListerAppelsOffre
from mauricette.application.cas_usage.obtenir_etat_traitement_appel_offre import (
    ObtenirEtatTraitementAppelOffre,
)
from mauricette.application.cas_usage.reanalyser_appel_offre import ReanalyserAppelOffre
from mauricette.application.cas_usage.relancer_document import RelancerDocument
from mauricette.application.cas_usage.lister_referentiels import ListerReferentiels
from mauricette.application.cas_usage.lister_referentiels_appel_offre import (
    ListerReferentielsAppelOffre,
)
from mauricette.application.cas_usage.lister_reponses_appel_offre import ListerReponsesAppelOffre
from mauricette.application.cas_usage.modifier_appel_offre import ModifierAppelOffre
from mauricette.application.cas_usage.modifier_question_referentiel import (
    ModifierQuestionReferentiel,
)
from mauricette.application.cas_usage.modifier_referentiel import ModifierReferentiel
from mauricette.application.cas_usage.modifier_section_referentiel import (
    ModifierSectionReferentiel,
)
from mauricette.application.cas_usage.obtenir_appel_offre import ObtenirAppelOffre
from mauricette.application.cas_usage.obtenir_referentiel_detail import ObtenirReferentielDetail
from mauricette.application.cas_usage.supprimer_document import SupprimerDocument
from mauricette.application.cas_usage.supprimer_question_referentiel import (
    SupprimerQuestionReferentiel,
)
from mauricette.application.cas_usage.supprimer_referentiel import SupprimerReferentiel
from mauricette.application.cas_usage.supprimer_section_referentiel import (
    SupprimerSectionReferentiel,
)
from mauricette.application.cas_usage.valider_reponse import ValiderReponse
from mauricette.config.parametres import obtenir_parametres
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
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort
from mauricette.infrastructure.persistence.postgres.appel_offre_repository_sql import (
    AppelOffreRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.base import GestionnaireSessions
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
from mauricette.infrastructure.rag.decoupeur_hierarchique import DecoupeurHierarchique
from mauricette.infrastructure.rag.docling_adapter import DoclingAdapter
from mauricette.infrastructure.rag.mistral_embedding_adapter import MistralEmbeddingAdapter
from mauricette.infrastructure.rag.mistral_generation_adapter import MistralGenerationAdapter
from mauricette.infrastructure.stockage.fabrique_stockage import creer_adaptateur_stockage


@lru_cache
def obtenir_gestionnaire_sessions() -> GestionnaireSessions:
    """Fournit le gestionnaire de sessions PostgreSQL, unique pour toute l'app."""
    return GestionnaireSessions(obtenir_parametres())


@lru_cache
def obtenir_stockage() -> StockageDocumentPort:
    """Fournit l'adaptateur de stockage de documents configuré (local ou S3/MinIO)."""
    return creer_adaptateur_stockage(obtenir_parametres())


@lru_cache
def obtenir_extracteur_document() -> ExtracteurDocumentPort:
    """Fournit l'adaptateur d'extraction de documents (Docling)."""
    return DoclingAdapter()


@lru_cache
def obtenir_decoupeur_document() -> DecoupeurDocumentPort:
    """Fournit l'adaptateur de découpage en chunks."""
    return DecoupeurHierarchique(obtenir_parametres())


@lru_cache
def obtenir_embedding() -> EmbeddingPort:
    """Fournit l'adaptateur d'embedding (Mistral)."""
    return MistralEmbeddingAdapter(obtenir_parametres())


@lru_cache
def obtenir_generation() -> GenerationReponsePort:
    """Fournit l'adaptateur de génération de réponses (Mistral Large)."""
    return MistralGenerationAdapter(obtenir_parametres())


def obtenir_session(
    gestionnaire: GestionnaireSessions = Depends(obtenir_gestionnaire_sessions),
) -> Iterator[Session]:
    """Fournit une session SQLAlchemy, fermée à la fin de la requête HTTP."""
    yield from gestionnaire.obtenir_session()


# --- Dépôts (repositories) ---


def obtenir_depot_appels_offre(
    session: Session = Depends(obtenir_session),
) -> AppelOffreRepositoryPort:
    """Fournit l'implémentation courante du port `AppelOffreRepositoryPort`."""
    return AppelOffreRepositorySQL(session)


def obtenir_depot_documents(
    session: Session = Depends(obtenir_session),
) -> DocumentRepositoryPort:
    """Fournit l'implémentation courante du port `DocumentRepositoryPort`."""
    return DocumentRepositorySQL(session)


def obtenir_depot_referentiels(
    session: Session = Depends(obtenir_session),
) -> ReferentielRepositoryPort:
    """Fournit l'implémentation courante du port `ReferentielRepositoryPort`."""
    return ReferentielRepositorySQL(session)


def obtenir_depot_sections(
    session: Session = Depends(obtenir_session),
) -> SectionReferentielRepositoryPort:
    """Fournit l'implémentation courante du port `SectionReferentielRepositoryPort`."""
    return SectionReferentielRepositorySQL(session)


def obtenir_depot_questions_referentiel(
    session: Session = Depends(obtenir_session),
) -> QuestionReferentielRepositoryPort:
    """Fournit l'implémentation courante du port `QuestionReferentielRepositoryPort`."""
    return QuestionReferentielRepositorySQL(session)


def obtenir_depot_referentiels_ao(
    session: Session = Depends(obtenir_session),
) -> ReferentielAppelOffreRepositoryPort:
    """Fournit l'implémentation courante du port `ReferentielAppelOffreRepositoryPort`."""
    return ReferentielAppelOffreRepositorySQL(session)


def obtenir_depot_traitement_rag(
    session: Session = Depends(obtenir_session),
) -> DocumentTraitementRagRepositoryPort:
    """Fournit l'implémentation courante du port `DocumentTraitementRagRepositoryPort`."""
    return DocumentTraitementRagRepositorySQL(session)


def obtenir_depot_chunks(
    session: Session = Depends(obtenir_session),
) -> ChunkRepositoryPort:
    """Fournit l'implémentation courante du port `ChunkRepositoryPort`."""
    return ChunkRepositorySQL(session)


def obtenir_depot_taches_traitement(
    session: Session = Depends(obtenir_session),
) -> TacheTraitementRepositoryPort:
    """Fournit l'implémentation courante du port `TacheTraitementRepositoryPort`."""
    return TacheTraitementRepositorySQL(session)


def obtenir_depot_reponses(
    session: Session = Depends(obtenir_session),
) -> ReponseQuestionRepositoryPort:
    """Fournit l'implémentation courante du port `ReponseQuestionRepositoryPort`."""
    return ReponseQuestionRepositorySQL(session)


# --- Appels d'Offres ---


def obtenir_cas_usage_creer_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_referentiels: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
) -> CreerAppelOffre:
    """Fournit le cas d'usage de création d'Appel d'Offres, prêt à l'emploi."""
    return CreerAppelOffre(depot_appels_offre, depot_referentiels, depot_referentiels_ao)


def obtenir_cas_usage_lister_appels_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> ListerAppelsOffre:
    """Fournit le cas d'usage de listing des Appels d'Offres, prêt à l'emploi."""
    return ListerAppelsOffre(depot_appels_offre, depot_documents)


def obtenir_cas_usage_modifier_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
) -> ModifierAppelOffre:
    """Fournit le cas d'usage de renommage d'un Appel d'Offres, prêt à l'emploi."""
    return ModifierAppelOffre(depot_appels_offre)


def obtenir_cas_usage_obtenir_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> ObtenirAppelOffre:
    """Fournit le cas d'usage de consultation d'un Appel d'Offres, prêt à l'emploi."""
    return ObtenirAppelOffre(depot_appels_offre, depot_documents)


def obtenir_cas_usage_deposer_document(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
    depot_traitement_rag: DocumentTraitementRagRepositoryPort = Depends(obtenir_depot_traitement_rag),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
    stockage: StockageDocumentPort = Depends(obtenir_stockage),
) -> DeposerDocument:
    """Fournit le cas d'usage de dépôt de document, prêt à l'emploi."""
    return DeposerDocument(
        depot_appels_offre, depot_documents, depot_traitement_rag, depot_taches, stockage
    )


def obtenir_cas_usage_deposer_fichier(
    deposer_document: DeposerDocument = Depends(obtenir_cas_usage_deposer_document),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> DeposerFichier:
    """Fournit le cas d'usage de dépôt de fichier (avec éclatement zip et dédoublonnage)."""
    return DeposerFichier(deposer_document, depot_documents)


def obtenir_cas_usage_supprimer_document(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
    stockage: StockageDocumentPort = Depends(obtenir_stockage),
) -> SupprimerDocument:
    """Fournit le cas d'usage de suppression d'un document, prêt à l'emploi."""
    return SupprimerDocument(depot_appels_offre, depot_documents, depot_taches, stockage)


# --- Référentiels ---


def obtenir_cas_usage_creer_referentiel(
    depot: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
) -> CreerReferentiel:
    """Fournit le cas d'usage de création d'un référentiel, prêt à l'emploi."""
    return CreerReferentiel(depot)


def obtenir_cas_usage_lister_referentiels(
    depot_referentiels: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
    depot_sections: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
    depot_questions: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
) -> ListerReferentiels:
    """Fournit le cas d'usage de listing des référentiels, prêt à l'emploi."""
    return ListerReferentiels(depot_referentiels, depot_sections, depot_questions, depot_referentiels_ao)


def obtenir_cas_usage_obtenir_referentiel_detail(
    depot_referentiels: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
    depot_sections: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
    depot_questions: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
) -> ObtenirReferentielDetail:
    """Fournit le cas d'usage de consultation détaillée d'un référentiel, prêt à l'emploi."""
    return ObtenirReferentielDetail(
        depot_referentiels, depot_sections, depot_questions, depot_referentiels_ao
    )


def obtenir_cas_usage_modifier_referentiel(
    depot: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
) -> ModifierReferentiel:
    """Fournit le cas d'usage de modification d'un référentiel, prêt à l'emploi."""
    return ModifierReferentiel(depot)


def obtenir_cas_usage_supprimer_referentiel(
    depot: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
) -> SupprimerReferentiel:
    """Fournit le cas d'usage de suppression d'un référentiel, prêt à l'emploi."""
    return SupprimerReferentiel(depot)


# --- Sections ---


def obtenir_cas_usage_creer_section(
    depot_sections: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
    depot_referentiels: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
) -> CreerSectionReferentiel:
    """Fournit le cas d'usage de création d'une section, prêt à l'emploi."""
    return CreerSectionReferentiel(depot_sections, depot_referentiels)


def obtenir_cas_usage_modifier_section(
    depot: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
) -> ModifierSectionReferentiel:
    """Fournit le cas d'usage de renommage d'une section, prêt à l'emploi."""
    return ModifierSectionReferentiel(depot)


def obtenir_cas_usage_supprimer_section(
    depot: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
) -> SupprimerSectionReferentiel:
    """Fournit le cas d'usage de suppression d'une section, prêt à l'emploi."""
    return SupprimerSectionReferentiel(depot)


# --- Questions de référentiel ---


def obtenir_cas_usage_creer_question_referentiel(
    depot_questions: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
    depot_sections: SectionReferentielRepositoryPort = Depends(obtenir_depot_sections),
) -> CreerQuestionReferentiel:
    """Fournit le cas d'usage de création d'une question, prêt à l'emploi."""
    return CreerQuestionReferentiel(depot_questions, depot_sections)


def obtenir_cas_usage_modifier_question_referentiel(
    depot: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
) -> ModifierQuestionReferentiel:
    """Fournit le cas d'usage de modification d'une question, prêt à l'emploi."""
    return ModifierQuestionReferentiel(depot)


def obtenir_cas_usage_changer_activation_question_referentiel(
    depot: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
) -> ChangerActivationQuestionReferentiel:
    """Fournit le cas d'usage d'archivage/réactivation d'une question, prêt à l'emploi."""
    return ChangerActivationQuestionReferentiel(depot)


def obtenir_cas_usage_supprimer_question_referentiel(
    depot: QuestionReferentielRepositoryPort = Depends(obtenir_depot_questions_referentiel),
) -> SupprimerQuestionReferentiel:
    """Fournit le cas d'usage de suppression d'une question, prêt à l'emploi."""
    return SupprimerQuestionReferentiel(depot)


# --- Rattachement référentiel ↔ Appel d'Offres ---


def obtenir_cas_usage_attacher_referentiel(
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_referentiels: ReferentielRepositoryPort = Depends(obtenir_depot_referentiels),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
) -> AttacherReferentielAAppelOffre:
    """Fournit le cas d'usage de rattachement d'un référentiel à un AO, prêt à l'emploi."""
    return AttacherReferentielAAppelOffre(
        depot_referentiels_ao, depot_appels_offre, depot_referentiels, depot_taches
    )


def obtenir_cas_usage_detacher_referentiel(
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
) -> DetacherReferentielDeAppelOffre:
    """Fournit le cas d'usage de détachement d'un référentiel d'un AO, prêt à l'emploi."""
    return DetacherReferentielDeAppelOffre(depot_referentiels_ao, depot_appels_offre, depot_taches)


def obtenir_cas_usage_lister_referentiels_ao(
    depot_referentiels_ao: ReferentielAppelOffreRepositoryPort = Depends(obtenir_depot_referentiels_ao),
) -> ListerReferentielsAppelOffre:
    """Fournit le cas d'usage de listing des référentiels rattachés à un AO, prêt à l'emploi."""
    return ListerReferentielsAppelOffre(depot_referentiels_ao)


# --- Traitement RAG ---
# Les cas d'usage par étape (ExtraireDocument, DecouperDocument, VectoriserDocument)
# ne sont consommés que par le worker RAG (infrastructure/worker/), pas par l'API :
# ils n'ont donc pas besoin d'un câblage `Depends()` ici.


def obtenir_cas_usage_relancer_document(
    depot_traitement_rag: DocumentTraitementRagRepositoryPort = Depends(obtenir_depot_traitement_rag),
    depot_chunks: ChunkRepositoryPort = Depends(obtenir_depot_chunks),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
) -> RelancerDocument:
    """Fournit le cas d'usage de relance d'un document en échec, prêt à l'emploi."""
    return RelancerDocument(depot_traitement_rag, depot_chunks, depot_taches)


def obtenir_cas_usage_obtenir_etat_traitement_ao(
    depot_traitement_rag: DocumentTraitementRagRepositoryPort = Depends(obtenir_depot_traitement_rag),
) -> ObtenirEtatTraitementAppelOffre:
    """Fournit le cas d'usage de consultation de l'état de traitement RAG d'un AO."""
    return ObtenirEtatTraitementAppelOffre(depot_traitement_rag)


def obtenir_cas_usage_lister_reponses_ao(
    depot_reponses: ReponseQuestionRepositoryPort = Depends(obtenir_depot_reponses),
) -> ListerReponsesAppelOffre:
    """Fournit le cas d'usage de consultation des réponses générées pour un AO."""
    return ListerReponsesAppelOffre(depot_reponses)


def obtenir_cas_usage_valider_reponse(
    depot_reponses: ReponseQuestionRepositoryPort = Depends(obtenir_depot_reponses),
) -> ValiderReponse:
    """Fournit le cas d'usage de validation manuelle d'une réponse générée."""
    return ValiderReponse(depot_reponses)


def obtenir_cas_usage_reanalyser_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_taches: TacheTraitementRepositoryPort = Depends(obtenir_depot_taches_traitement),
) -> ReanalyserAppelOffre:
    """Fournit le cas d'usage de relance manuelle de l'analyse d'un AO, prêt à l'emploi."""
    return ReanalyserAppelOffre(depot_appels_offre, depot_taches)
