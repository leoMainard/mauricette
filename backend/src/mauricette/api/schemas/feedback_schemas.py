"""Schémas Pydantic (contrats HTTP) pour le feedback utilisateur (général et par réponse)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mauricette.application.cas_usage.obtenir_statistiques_feedback import StatistiquesFeedback
from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback
from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.entites.feedback_reponse import FeedbackReponse
from mauricette.domaine.ports.feedback_reponse_repository import FeedbackReponseDetaille


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
    sources_attendues_ids: list[UUID] = []
    citation_attendue: str | None = None
    types_erreur: list[TypeErreurFeedback] = []
    details_erreur: str | None = None


class FeedbackReponseReponse(BaseModel):
    """Représentation HTTP du feedback sur la réponse à une question de référentiel."""

    id: UUID
    appel_offre_id: UUID
    question_referentiel_id: UUID
    avis: Avis | None
    contenu_reponse_snapshot: str | None
    commentaire: str | None
    sources_attendues_ids: list[UUID]
    citation_attendue: str | None
    types_erreur: list[TypeErreurFeedback]
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
            sources_attendues_ids=entite.sources_attendues_ids,
            citation_attendue=entite.citation_attendue,
            types_erreur=entite.types_erreur,
            details_erreur=entite.details_erreur,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )


class FeedbackReponseDetailleReponse(BaseModel):
    """Un feedback par réponse enrichi de son contexte (AO, référentiel, question),
    pour l'analyse et le filtrage détaillés du tableau de bord admin."""

    id: UUID
    appel_offre_id: UUID
    appel_offre_nom: str
    referentiel_id: UUID
    referentiel_nom: str
    question_referentiel_id: UUID
    question: str
    avis: Avis | None
    commentaire: str | None
    contenu_reponse_snapshot: str | None
    sources_attendues_ids: list[UUID]
    sources_attendues_noms: list[str]
    citation_attendue: str | None
    types_erreur: list[TypeErreurFeedback]
    details_erreur: str | None
    date_creation: datetime

    @classmethod
    def depuis_dto(cls, dto: FeedbackReponseDetaille) -> "FeedbackReponseDetailleReponse":
        return cls(
            id=dto.id,
            appel_offre_id=dto.appel_offre_id,
            appel_offre_nom=dto.appel_offre_nom,
            referentiel_id=dto.referentiel_id,
            referentiel_nom=dto.referentiel_nom,
            question_referentiel_id=dto.question_referentiel_id,
            question=dto.question,
            avis=dto.avis,
            commentaire=dto.commentaire,
            contenu_reponse_snapshot=dto.contenu_reponse_snapshot,
            sources_attendues_ids=dto.sources_attendues_ids,
            sources_attendues_noms=dto.sources_attendues_noms,
            citation_attendue=dto.citation_attendue,
            types_erreur=dto.types_erreur,
            details_erreur=dto.details_erreur,
            date_creation=dto.date_creation,
        )


class StatistiquesFeedbackReponse(BaseModel):
    """Statistiques globales de feedback (tous AO confondus), pour le tableau de bord admin."""

    general_par_avis: dict[str, int]
    reponse_par_avis: dict[str, int]
    general_bruts: list[FeedbackGeneralReponse]
    reponse_negatifs_par_referentiel: dict[UUID, int]
    reponse_detailles: list[FeedbackReponseDetailleReponse]

    @classmethod
    def depuis_dto(cls, dto: StatistiquesFeedback) -> "StatistiquesFeedbackReponse":
        return cls(
            general_par_avis=dto.general_par_avis,
            reponse_par_avis=dto.reponse_par_avis,
            general_bruts=[FeedbackGeneralReponse.depuis_entite(f) for f in dto.general_bruts],
            reponse_negatifs_par_referentiel=dto.reponse_negatifs_par_referentiel,
            reponse_detailles=[
                FeedbackReponseDetailleReponse.depuis_dto(f) for f in dto.reponse_detailles
            ],
        )
