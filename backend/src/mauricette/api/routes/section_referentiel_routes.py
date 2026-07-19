"""Routes HTTP relatives aux sections de référentiel."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_creer_question_referentiel,
    obtenir_cas_usage_modifier_section,
    obtenir_cas_usage_supprimer_section,
)
from mauricette.api.schemas.referentiel_schemas import (
    ContenuQuestionReferentielRequete,
    ModificationSectionRequete,
    QuestionReferentielReponse,
    SectionReponse,
)
from mauricette.application.cas_usage.creer_question_referentiel import (
    CommandeCreerQuestionReferentiel,
    CreerQuestionReferentiel,
)
from mauricette.application.cas_usage.modifier_section_referentiel import (
    CommandeModifierSection,
    ModifierSectionReferentiel,
)
from mauricette.application.cas_usage.supprimer_section_referentiel import (
    SupprimerSectionReferentiel,
)
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/sections", tags=["Sections de référentiel"])


@routeur.patch("/{section_id}", response_model=SectionReponse)
def modifier_section(
    section_id: UUID,
    requete: ModificationSectionRequete,
    cas_usage: ModifierSectionReferentiel = Depends(obtenir_cas_usage_modifier_section),
) -> SectionReponse:
    """Renomme une section existante."""
    try:
        section = cas_usage.executer(CommandeModifierSection(section_id=section_id, nom=requete.nom))
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return SectionReponse.depuis_entite(section)


@routeur.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_section(
    section_id: UUID,
    cas_usage: SupprimerSectionReferentiel = Depends(obtenir_cas_usage_supprimer_section),
) -> None:
    """Supprime définitivement une section (et ses questions)."""
    try:
        cas_usage.executer(section_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur


@routeur.post(
    "/{section_id}/questions", response_model=QuestionReferentielReponse, status_code=status.HTTP_201_CREATED
)
def creer_question(
    section_id: UUID,
    requete: ContenuQuestionReferentielRequete,
    cas_usage: CreerQuestionReferentiel = Depends(obtenir_cas_usage_creer_question_referentiel),
) -> QuestionReferentielReponse:
    """Crée une nouvelle question dans une section."""
    try:
        question = cas_usage.executer(
            CommandeCreerQuestionReferentiel(
                section_id=section_id,
                question=requete.question,
                format_reponse=requete.format_reponse,
                aide_extraction=requete.aide_extraction,
                obligatoire=requete.obligatoire,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return QuestionReferentielReponse.depuis_entite(question)
