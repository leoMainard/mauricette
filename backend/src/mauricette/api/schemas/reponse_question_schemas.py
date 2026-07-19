"""Schémas Pydantic (contrats HTTP) pour les réponses générées aux questions de référentiel."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mauricette.domaine.entites.reponse_question import Citation, ReponseQuestion
from mauricette.domaine.entites.enums import StatutReponse


class CitationReponse(BaseModel):
    """Représentation HTTP d'une citation (chunk source d'une réponse générée)."""

    chunk_id: UUID
    document_id: UUID
    document_nom: str
    page_debut: int | None
    page_fin: int | None
    titre_section: str | None

    @classmethod
    def depuis_entite(cls, citation: Citation) -> "CitationReponse":
        return cls(
            chunk_id=citation.chunk_id,
            document_id=citation.document_id,
            document_nom=citation.document_nom,
            page_debut=citation.page_debut,
            page_fin=citation.page_fin,
            titre_section=citation.titre_section,
        )


class ReponseQuestionReponse(BaseModel):
    """Représentation HTTP d'une réponse générée pour une question de référentiel."""

    id: UUID
    appel_offre_id: UUID
    question_referentiel_id: UUID
    contenu: str | None
    score_confiance: float | None
    statut: StatutReponse
    citations: list[CitationReponse]
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: ReponseQuestion) -> "ReponseQuestionReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            appel_offre_id=entite.appel_offre_id,
            question_referentiel_id=entite.question_referentiel_id,
            contenu=entite.contenu,
            score_confiance=entite.score_confiance,
            statut=entite.statut,
            citations=[CitationReponse.depuis_entite(c) for c in entite.citations],
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )
