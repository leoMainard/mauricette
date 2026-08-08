"""Routes HTTP relatives au feedback utilisateur (général par AO et par réponse)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_enregistrer_feedback_general,
    obtenir_cas_usage_enregistrer_feedback_reponse,
    obtenir_cas_usage_lister_feedback_reponses,
    obtenir_cas_usage_obtenir_feedback_general,
)
from mauricette.api.schemas.feedback_schemas import (
    FeedbackGeneralReponse,
    FeedbackGeneralRequete,
    FeedbackReponseReponse,
    FeedbackReponseRequete,
)
from mauricette.application.cas_usage.enregistrer_feedback_general import (
    CommandeEnregistrerFeedbackGeneral,
    EnregistrerFeedbackGeneral,
)
from mauricette.application.cas_usage.enregistrer_feedback_reponse import (
    CommandeEnregistrerFeedbackReponse,
    EnregistrerFeedbackReponse,
)
from mauricette.application.cas_usage.lister_feedback_reponses import ListerFeedbackReponses
from mauricette.application.cas_usage.obtenir_feedback_general import ObtenirFeedbackGeneral
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}", tags=["Feedback"])


@routeur.get("/feedback", response_model=FeedbackGeneralReponse | None)
def obtenir_feedback_general(
    appel_offre_id: UUID,
    cas_usage: ObtenirFeedbackGeneral = Depends(obtenir_cas_usage_obtenir_feedback_general),
) -> FeedbackGeneralReponse | None:
    """Retourne le feedback général de l'AO, s'il en existe un."""
    try:
        feedback = cas_usage.executer(appel_offre_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return FeedbackGeneralReponse.depuis_entite(feedback) if feedback else None


@routeur.put("/feedback", response_model=FeedbackGeneralReponse)
def enregistrer_feedback_general(
    appel_offre_id: UUID,
    requete: FeedbackGeneralRequete,
    cas_usage: EnregistrerFeedbackGeneral = Depends(obtenir_cas_usage_enregistrer_feedback_general),
) -> FeedbackGeneralReponse:
    """Enregistre (crée ou remplace) le feedback général de l'AO."""
    try:
        feedback = cas_usage.executer(
            CommandeEnregistrerFeedbackGeneral(
                appel_offre_id=appel_offre_id,
                avis=requete.avis,
                commentaire=requete.commentaire,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return FeedbackGeneralReponse.depuis_entite(feedback)


@routeur.get("/feedback-reponses", response_model=list[FeedbackReponseReponse])
def lister_feedback_reponses(
    appel_offre_id: UUID,
    cas_usage: ListerFeedbackReponses = Depends(obtenir_cas_usage_lister_feedback_reponses),
) -> list[FeedbackReponseReponse]:
    """Retourne tous les feedbacks de réponses enregistrés pour l'AO."""
    try:
        feedbacks = cas_usage.executer(appel_offre_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return [FeedbackReponseReponse.depuis_entite(feedback) for feedback in feedbacks]


@routeur.put(
    "/feedback-reponses/{question_referentiel_id}",
    response_model=FeedbackReponseReponse,
)
def enregistrer_feedback_reponse(
    appel_offre_id: UUID,
    question_referentiel_id: UUID,
    requete: FeedbackReponseRequete,
    cas_usage: EnregistrerFeedbackReponse = Depends(obtenir_cas_usage_enregistrer_feedback_reponse),
) -> FeedbackReponseReponse:
    """Enregistre (crée ou remplace) le feedback sur la réponse à une question de référentiel."""
    try:
        feedback = cas_usage.executer(
            CommandeEnregistrerFeedbackReponse(
                appel_offre_id=appel_offre_id,
                question_referentiel_id=question_referentiel_id,
                avis=requete.avis,
                commentaire=requete.commentaire,
                sources_attendues_ids=requete.sources_attendues_ids,
                citation_attendue=requete.citation_attendue,
                types_erreur=requete.types_erreur,
                details_erreur=requete.details_erreur,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return FeedbackReponseReponse.depuis_entite(feedback)
