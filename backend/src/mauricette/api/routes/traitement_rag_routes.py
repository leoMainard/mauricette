"""Routes HTTP pour le suivi et la relance du traitement RAG des documents d'un AO."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_lister_reponses_ao,
    obtenir_cas_usage_obtenir_etat_traitement_ao,
    obtenir_cas_usage_relancer_document,
    obtenir_cas_usage_valider_reponse,
)
from mauricette.api.schemas.reponse_question_schemas import ReponseQuestionReponse
from mauricette.api.schemas.traitement_rag_schemas import DocumentTraitementRagReponse
from mauricette.application.cas_usage.lister_reponses_appel_offre import ListerReponsesAppelOffre
from mauricette.application.cas_usage.obtenir_etat_traitement_appel_offre import (
    ObtenirEtatTraitementAppelOffre,
)
from mauricette.application.cas_usage.relancer_document import (
    CommandeRelancerDocument,
    RelancerDocument,
)
from mauricette.application.cas_usage.valider_reponse import CommandeValiderReponse, ValiderReponse
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurEtatTraitementInvalide

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}", tags=["Traitement RAG"])
routeur_reponses = APIRouter(prefix="/reponses", tags=["Réponses RAG"])


@routeur.get("/traitement", response_model=list[DocumentTraitementRagReponse])
def obtenir_etat_traitement(
    appel_offre_id: UUID,
    cas_usage: ObtenirEtatTraitementAppelOffre = Depends(obtenir_cas_usage_obtenir_etat_traitement_ao),
) -> list[DocumentTraitementRagReponse]:
    """Retourne l'état du pipeline RAG pour chaque document de l'Appel d'Offres."""
    return [DocumentTraitementRagReponse.depuis_entite(t) for t in cas_usage.executer(appel_offre_id)]


@routeur.post("/documents/{document_id}/traitement/relancer", status_code=status.HTTP_202_ACCEPTED)
def relancer_traitement_document(
    appel_offre_id: UUID,
    document_id: UUID,
    cas_usage: RelancerDocument = Depends(obtenir_cas_usage_relancer_document),
) -> None:
    """Relance depuis le début le traitement RAG d'un document en échec."""
    try:
        cas_usage.executer(CommandeRelancerDocument(appel_offre_id=appel_offre_id, document_id=document_id))
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except ErreurEtatTraitementInvalide as erreur:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erreur)) from erreur


@routeur.get("/reponses", response_model=list[ReponseQuestionReponse])
def lister_reponses(
    appel_offre_id: UUID,
    cas_usage: ListerReponsesAppelOffre = Depends(obtenir_cas_usage_lister_reponses_ao),
) -> list[ReponseQuestionReponse]:
    """Retourne les réponses générées pour les questions de référentiel de l'Appel d'Offres."""
    return [ReponseQuestionReponse.depuis_entite(r) for r in cas_usage.executer(appel_offre_id)]


@routeur_reponses.patch("/{reponse_id}/valider", response_model=ReponseQuestionReponse)
def valider_reponse(
    reponse_id: UUID,
    cas_usage: ValiderReponse = Depends(obtenir_cas_usage_valider_reponse),
) -> ReponseQuestionReponse:
    """Marque une réponse générée comme validée par un utilisateur humain."""
    try:
        reponse = cas_usage.executer(CommandeValiderReponse(reponse_id=reponse_id))
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return ReponseQuestionReponse.depuis_entite(reponse)
