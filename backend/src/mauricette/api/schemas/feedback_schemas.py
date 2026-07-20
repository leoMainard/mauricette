"""Schémas Pydantic (contrats HTTP) pour le feedback utilisateur (général et par réponse)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback
from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.entites.feedback_reponse import FeedbackReponse


class FeedbackGeneralRequete(BaseModel):
    """Corps de requête pour enregistrer le feedback général d'un AO."""

    avis: Avis | None = None
    commentaire: str | None = None


class FeedbackGeneralReponse(BaseModel):
    """Représentation HTTP du feedback général d'un AO."""

    id: UUID
    appel_offre_id: UUID
    avis: Avis | None
    commentaire: str | None
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: FeedbackGeneral) -> "FeedbackGeneralReponse":
        return cls(
            id=entite.id,
            appel_offre_id=entite.appel_offre_id,
            avis=entite.avis,
            commentaire=entite.commentaire,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )


class FeedbackReponseRequete(BaseModel):
    """Corps de requête pour enregistrer le feedback sur la réponse à une question de référentiel."""

    avis: Avis | None = None
    commentaire: str | None = None
    source_attendue: str | None = None
    citation_attendue: str | None = None
    type_erreur: TypeErreurFeedback | None = None
    details_erreur: str | None = None


class FeedbackReponseReponse(BaseModel):
    """Représentation HTTP du feedback sur la réponse à une question de référentiel."""

    id: UUID
    appel_offre_id: UUID
    question_referentiel_id: UUID
    avis: Avis | None
    contenu_reponse_snapshot: str | None
    commentaire: str | None
    source_attendue: str | None
    citation_attendue: str | None
    type_erreur: TypeErreurFeedback | None
    details_erreur: str | None
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: FeedbackReponse) -> "FeedbackReponseReponse":
        return cls(
            id=entite.id,
            appel_offre_id=entite.appel_offre_id,
            question_referentiel_id=entite.question_referentiel_id,
            avis=entite.avis,
            contenu_reponse_snapshot=entite.contenu_reponse_snapshot,
            commentaire=entite.commentaire,
            source_attendue=entite.source_attendue,
            citation_attendue=entite.citation_attendue,
            type_erreur=entite.type_erreur,
            details_erreur=entite.details_erreur,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )
