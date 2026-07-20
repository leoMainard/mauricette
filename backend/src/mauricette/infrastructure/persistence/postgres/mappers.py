"""Conversion entre modèles ORM (SQLAlchemy) et entités du domaine.

Isoler ce mapping ici évite de polluer le domaine avec des détails de
persistance, et évite de polluer les modèles ORM avec de la logique métier.
"""

from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.chunk import Chunk
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag
from mauricette.domaine.entites.enums import (
    FormatReponse,
    FournisseurStockage,
    RoleMessageChatbot,
    StatutAppelOffre,
    StatutDocument,
    StatutEtape,
    StatutReponse,
    StatutTache,
    TypeChunk,
    TypeTache,
)
from mauricette.domaine.entites.message_chatbot import MessageChatbot
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.entites.reponse_question import Citation, ReponseQuestion
from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.entites.tache_traitement import TacheTraitement
from mauricette.infrastructure.persistence.postgres.modeles import (
    AppelOffreModele,
    ChunkModele,
    DocumentModele,
    DocumentTraitementRagModele,
    MessageChatbotModele,
    QuestionReferentielModele,
    ReferentielModele,
    ReponseQuestionModele,
    SectionReferentielModele,
    TacheTraitementModele,
)


def appel_offre_vers_entite(modele: AppelOffreModele) -> AppelOffre:
    """Convertit un modèle ORM `AppelOffreModele` en entité de domaine `AppelOffre`."""
    return AppelOffre(
        id=modele.id,
        nom=modele.nom,
        cree_par=modele.cree_par,
        statut=StatutAppelOffre(modele.statut),
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def appel_offre_vers_modele(entite: AppelOffre) -> AppelOffreModele:
    """Convertit une entité de domaine `AppelOffre` en modèle ORM `AppelOffreModele`."""
    return AppelOffreModele(
        id=entite.id,
        nom=entite.nom,
        cree_par=entite.cree_par,
        statut=entite.statut.value,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def document_vers_entite(modele: DocumentModele) -> Document:
    """Convertit un modèle ORM `DocumentModele` en entité de domaine `Document`."""
    return Document(
        id=modele.id,
        appel_offre_id=modele.appel_offre_id,
        nom_original=modele.nom_original,
        cle_stockage=modele.cle_stockage,
        fournisseur_stockage=FournisseurStockage(modele.fournisseur_stockage),
        type_mime=modele.type_mime,
        taille_octets=modele.taille_octets,
        hash_sha256=modele.hash_sha256,
        statut=StatutDocument(modele.statut),
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def document_vers_modele(entite: Document) -> DocumentModele:
    """Convertit une entité de domaine `Document` en modèle ORM `DocumentModele`."""
    return DocumentModele(
        id=entite.id,
        appel_offre_id=entite.appel_offre_id,
        nom_original=entite.nom_original,
        cle_stockage=entite.cle_stockage,
        fournisseur_stockage=entite.fournisseur_stockage.value,
        type_mime=entite.type_mime,
        taille_octets=entite.taille_octets,
        hash_sha256=entite.hash_sha256,
        statut=entite.statut.value,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def referentiel_vers_entite(modele: ReferentielModele) -> Referentiel:
    """Convertit un modèle ORM `ReferentielModele` en entité de domaine `Referentiel`."""
    return Referentiel(
        id=modele.id,
        nom=modele.nom,
        description=modele.description,
        actif_par_defaut=modele.actif_par_defaut,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def referentiel_vers_modele(entite: Referentiel) -> ReferentielModele:
    """Convertit une entité de domaine `Referentiel` en modèle ORM `ReferentielModele`."""
    return ReferentielModele(
        id=entite.id,
        nom=entite.nom,
        description=entite.description,
        actif_par_defaut=entite.actif_par_defaut,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def section_referentiel_vers_entite(modele: SectionReferentielModele) -> SectionReferentiel:
    """Convertit un modèle ORM `SectionReferentielModele` en entité de domaine."""
    return SectionReferentiel(
        id=modele.id,
        referentiel_id=modele.referentiel_id,
        nom=modele.nom,
        ordre=modele.ordre,
        date_creation=modele.date_creation,
    )


def section_referentiel_vers_modele(entite: SectionReferentiel) -> SectionReferentielModele:
    """Convertit une entité de domaine `SectionReferentiel` en modèle ORM."""
    return SectionReferentielModele(
        id=entite.id,
        referentiel_id=entite.referentiel_id,
        nom=entite.nom,
        ordre=entite.ordre,
        date_creation=entite.date_creation,
    )


def question_referentiel_vers_entite(modele: QuestionReferentielModele) -> QuestionReferentiel:
    """Convertit un modèle ORM `QuestionReferentielModele` en entité de domaine."""
    return QuestionReferentiel(
        id=modele.id,
        section_id=modele.section_id,
        question=modele.question,
        format_reponse=FormatReponse(modele.format_reponse),
        aide_extraction=modele.aide_extraction,
        obligatoire=modele.obligatoire,
        actif=modele.actif,
        ordre=modele.ordre,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def question_referentiel_vers_modele(entite: QuestionReferentiel) -> QuestionReferentielModele:
    """Convertit une entité de domaine `QuestionReferentiel` en modèle ORM."""
    return QuestionReferentielModele(
        id=entite.id,
        section_id=entite.section_id,
        question=entite.question,
        format_reponse=entite.format_reponse.value,
        aide_extraction=entite.aide_extraction,
        obligatoire=entite.obligatoire,
        actif=entite.actif,
        ordre=entite.ordre,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def document_traitement_rag_vers_entite(modele: DocumentTraitementRagModele) -> DocumentTraitementRag:
    """Convertit un modèle ORM `DocumentTraitementRagModele` en entité de domaine."""
    return DocumentTraitementRag(
        document_id=modele.document_id,
        appel_offre_id=modele.appel_offre_id,
        extraction_statut=StatutEtape(modele.extraction_statut),
        extraction_message_erreur=modele.extraction_message_erreur,
        extraction_date_maj=modele.extraction_date_maj,
        decoupage_statut=StatutEtape(modele.decoupage_statut),
        decoupage_message_erreur=modele.decoupage_message_erreur,
        decoupage_date_maj=modele.decoupage_date_maj,
        embedding_statut=StatutEtape(modele.embedding_statut),
        embedding_message_erreur=modele.embedding_message_erreur,
        embedding_date_maj=modele.embedding_date_maj,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def document_traitement_rag_vers_modele(entite: DocumentTraitementRag) -> DocumentTraitementRagModele:
    """Convertit une entité de domaine `DocumentTraitementRag` en modèle ORM."""
    return DocumentTraitementRagModele(
        document_id=entite.document_id,
        appel_offre_id=entite.appel_offre_id,
        extraction_statut=entite.extraction_statut.value,
        extraction_message_erreur=entite.extraction_message_erreur,
        extraction_date_maj=entite.extraction_date_maj,
        decoupage_statut=entite.decoupage_statut.value,
        decoupage_message_erreur=entite.decoupage_message_erreur,
        decoupage_date_maj=entite.decoupage_date_maj,
        embedding_statut=entite.embedding_statut.value,
        embedding_message_erreur=entite.embedding_message_erreur,
        embedding_date_maj=entite.embedding_date_maj,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def chunk_vers_entite(modele: ChunkModele) -> Chunk:
    """Convertit un modèle ORM `ChunkModele` en entité de domaine `Chunk`."""
    return Chunk(
        id=modele.id,
        document_id=modele.document_id,
        appel_offre_id=modele.appel_offre_id,
        contenu=modele.contenu,
        type_chunk=TypeChunk(modele.type_chunk),
        page_debut=modele.page_debut,
        page_fin=modele.page_fin,
        titre_section=modele.titre_section,
        ordre=modele.ordre,
        embedding=list(modele.embedding) if modele.embedding is not None else None,
        date_creation=modele.date_creation,
    )


def chunk_vers_modele(entite: Chunk) -> ChunkModele:
    """Convertit une entité de domaine `Chunk` en modèle ORM `ChunkModele`."""
    return ChunkModele(
        id=entite.id,
        document_id=entite.document_id,
        appel_offre_id=entite.appel_offre_id,
        contenu=entite.contenu,
        type_chunk=entite.type_chunk.value,
        page_debut=entite.page_debut,
        page_fin=entite.page_fin,
        titre_section=entite.titre_section,
        ordre=entite.ordre,
        embedding=entite.embedding,
        date_creation=entite.date_creation,
    )


def tache_traitement_vers_entite(modele: TacheTraitementModele) -> TacheTraitement:
    """Convertit un modèle ORM `TacheTraitementModele` en entité de domaine `TacheTraitement`."""
    return TacheTraitement(
        id=modele.id,
        type_tache=TypeTache(modele.type_tache),
        reference_id=modele.reference_id,
        statut=StatutTache(modele.statut),
        tentatives=modele.tentatives,
        message_erreur=modele.message_erreur,
        date_prochaine_tentative=modele.date_prochaine_tentative,
        date_reservation=modele.date_reservation,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def tache_traitement_vers_modele(entite: TacheTraitement) -> TacheTraitementModele:
    """Convertit une entité de domaine `TacheTraitement` en modèle ORM `TacheTraitementModele`."""
    return TacheTraitementModele(
        id=entite.id,
        type_tache=entite.type_tache.value,
        reference_id=entite.reference_id,
        statut=entite.statut.value,
        tentatives=entite.tentatives,
        message_erreur=entite.message_erreur,
        date_prochaine_tentative=entite.date_prochaine_tentative,
        date_reservation=entite.date_reservation,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def _citation_vers_dict(citation: Citation) -> dict:
    return {
        "chunk_id": str(citation.chunk_id),
        "document_id": str(citation.document_id),
        "document_nom": citation.document_nom,
        "page_debut": citation.page_debut,
        "page_fin": citation.page_fin,
        "titre_section": citation.titre_section,
    }


def _citation_depuis_dict(donnees: dict) -> Citation:
    return Citation(
        chunk_id=UUID(donnees["chunk_id"]),
        document_id=UUID(donnees["document_id"]),
        document_nom=donnees["document_nom"],
        page_debut=donnees["page_debut"],
        page_fin=donnees["page_fin"],
        titre_section=donnees["titre_section"],
    )


def reponse_question_vers_entite(modele: ReponseQuestionModele) -> ReponseQuestion:
    """Convertit un modèle ORM `ReponseQuestionModele` en entité de domaine `ReponseQuestion`."""
    return ReponseQuestion(
        id=modele.id,
        appel_offre_id=modele.appel_offre_id,
        question_referentiel_id=modele.question_referentiel_id,
        contenu=modele.contenu,
        score_confiance=modele.score_confiance,
        statut=StatutReponse(modele.statut),
        citations=[_citation_depuis_dict(c) for c in modele.citations],
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def reponse_question_vers_modele(entite: ReponseQuestion) -> ReponseQuestionModele:
    """Convertit une entité de domaine `ReponseQuestion` en modèle ORM `ReponseQuestionModele`."""
    return ReponseQuestionModele(
        id=entite.id,
        appel_offre_id=entite.appel_offre_id,
        question_referentiel_id=entite.question_referentiel_id,
        contenu=entite.contenu,
        score_confiance=entite.score_confiance,
        statut=entite.statut.value,
        citations=[_citation_vers_dict(c) for c in entite.citations],
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def message_chatbot_vers_entite(modele: MessageChatbotModele) -> MessageChatbot:
    """Convertit un modèle ORM `MessageChatbotModele` en entité de domaine `MessageChatbot`."""
    return MessageChatbot(
        id=modele.id,
        appel_offre_id=modele.appel_offre_id,
        role=RoleMessageChatbot(modele.role),
        contenu=modele.contenu,
        score_confiance=modele.score_confiance,
        citations=[_citation_depuis_dict(c) for c in modele.citations],
        date_creation=modele.date_creation,
    )


def message_chatbot_vers_modele(entite: MessageChatbot) -> MessageChatbotModele:
    """Convertit une entité de domaine `MessageChatbot` en modèle ORM `MessageChatbotModele`."""
    return MessageChatbotModele(
        id=entite.id,
        appel_offre_id=entite.appel_offre_id,
        role=entite.role.value,
        contenu=entite.contenu,
        score_confiance=entite.score_confiance,
        citations=[_citation_vers_dict(c) for c in entite.citations],
        date_creation=entite.date_creation,
    )
