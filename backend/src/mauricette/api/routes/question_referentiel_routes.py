"""Routes HTTP relatives aux questions de référentiel."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_changer_activation_question_referentiel,
    obtenir_cas_usage_modifier_question_referentiel,
    obtenir_cas_usage_supprimer_question_referentiel,
)
from mauricette.api.schemas.referentiel_schemas import (
    ContenuQuestionReferentielRequete,
    ModificationActivationQuestionRequete,
    QuestionReferentielReponse,
)
from mauricette.application.cas_usage.changer_activation_question_referentiel import (
    ChangerActivationQuestionReferentiel,
    CommandeChangerActivationQuestion,
)
from mauricette.application.cas_usage.modifier_question_referentiel import (
    CommandeModifierQuestionReferentiel,
    ModifierQuestionReferentiel,
)
from mauricette.application.cas_usage.supprimer_question_referentiel import (
    SupprimerQuestionReferentiel,
)
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/questions", tags=["Questions de référentiel"])


@routeur.patch("/{question_id}", response_model=QuestionReferentielReponse)
def modifier_question(
    question_id: UUID,
    requete: ContenuQuestionReferentielRequete,
    cas_usage: ModifierQuestionReferentiel = Depends(obtenir_cas_usage_modifier_question_referentiel),
) -> QuestionReferentielReponse:
    """Modifie le contenu d'une question existante."""
    try:
        question = cas_usage.executer(
            CommandeModifierQuestionReferentiel(
                question_id=question_id,
                question=requete.question,
                format_reponse=requete.format_reponse,
                aide_extraction=requete.aide_extraction,
                obligatoire=requete.obligatoire,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return QuestionReferentielReponse.depuis_entite(question)


@routeur.patch("/{question_id}/activation", response_model=QuestionReferentielReponse)
def changer_activation_question(
    question_id: UUID,
    requete: ModificationActivationQuestionRequete,
    cas_usage: ChangerActivationQuestionReferentiel = Depends(
        obtenir_cas_usage_changer_activation_question_referentiel
    ),
) -> QuestionReferentielReponse:
    """Archive ou réactive une question."""
    try:
        question = cas_usage.executer(
            CommandeChangerActivationQuestion(question_id=question_id, actif=requete.actif)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return QuestionReferentielReponse.depuis_entite(question)


@routeur.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_question(
    question_id: UUID,
    cas_usage: SupprimerQuestionReferentiel = Depends(obtenir_cas_usage_supprimer_question_referentiel),
) -> None:
    """Supprime définitivement une question."""
    try:
        cas_usage.executer(question_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
