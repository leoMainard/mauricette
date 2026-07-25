"""Routes HTTP relatives aux référentiels et à leurs sections."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mauricette.api.dependances import (
    obtenir_cas_usage_creer_referentiel,
    obtenir_cas_usage_creer_section,
    obtenir_cas_usage_lister_referentiels,
    obtenir_cas_usage_modifier_referentiel,
    obtenir_cas_usage_obtenir_referentiel_detail,
    obtenir_cas_usage_reordonner_sections,
    obtenir_cas_usage_supprimer_referentiel,
    obtenir_ids_proprietaires_visibles,
    obtenir_utilisateur_courant,
)
from mauricette.api.schemas.referentiel_schemas import (
    CreationReferentielRequete,
    CreationSectionRequete,
    DetailReferentielReponse,
    ModificationReferentielRequete,
    ReferentielAvecStatistiquesReponse,
    ReferentielReponse,
    ReordonnerSectionsRequete,
    SectionReponse,
)
from mauricette.application.cas_usage.creer_referentiel import (
    CommandeCreerReferentiel,
    CreerReferentiel,
)
from mauricette.application.cas_usage.creer_section_referentiel import (
    CommandeCreerSection,
    CreerSectionReferentiel,
)
from mauricette.application.cas_usage.lister_referentiels import ListerReferentiels
from mauricette.application.cas_usage.modifier_referentiel import (
    CommandeModifierReferentiel,
    ModifierReferentiel,
)
from mauricette.application.cas_usage.obtenir_referentiel_detail import ObtenirReferentielDetail
from mauricette.application.cas_usage.reordonner_sections_referentiel import (
    CommandeReordonnerSections,
    ReordonnerSectionsReferentiel,
)
from mauricette.application.cas_usage.supprimer_referentiel import SupprimerReferentiel
from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurValidationDomaine

routeur = APIRouter(prefix="/referentiels", tags=["Référentiels"])


@routeur.post("", response_model=ReferentielReponse, status_code=status.HTTP_201_CREATED)
def creer_referentiel(
    requete: CreationReferentielRequete,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
    cas_usage: CreerReferentiel = Depends(obtenir_cas_usage_creer_referentiel),
) -> ReferentielReponse:
    """Crée un nouveau référentiel, rattaché à l'utilisateur connecté."""
    referentiel = cas_usage.executer(
        CommandeCreerReferentiel(
            nom=requete.nom,
            cree_par_id=utilisateur.id,
            description=requete.description,
            actif_par_defaut=requete.actif_par_defaut,
        )
    )
    return ReferentielReponse.depuis_entite(referentiel)


@routeur.get("", response_model=list[ReferentielAvecStatistiquesReponse])
def lister_referentiels(
    recherche: str | None = Query(default=None, description="Filtre les référentiels par nom"),
    ids_proprietaires_visibles: list[UUID] = Depends(obtenir_ids_proprietaires_visibles),
    cas_usage: ListerReferentiels = Depends(obtenir_cas_usage_lister_referentiels),
) -> list[ReferentielAvecStatistiquesReponse]:
    """Liste les référentiels visibles par l'utilisateur connecté (les siens, plus
    ceux de son groupe le cas échéant), triés par nom, avec leurs statistiques."""
    return [
        ReferentielAvecStatistiquesReponse.depuis_dto(dto)
        for dto in cas_usage.executer(recherche, ids_proprietaires_visibles)
    ]


@routeur.get("/{referentiel_id}", response_model=DetailReferentielReponse)
def obtenir_referentiel(
    referentiel_id: UUID,
    cas_usage: ObtenirReferentielDetail = Depends(obtenir_cas_usage_obtenir_referentiel_detail),
) -> DetailReferentielReponse:
    """Retourne le détail complet d'un référentiel (sections et questions incluses)."""
    try:
        detail = cas_usage.executer(referentiel_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return DetailReferentielReponse.depuis_dto(detail)


@routeur.patch("/{referentiel_id}", response_model=ReferentielReponse)
def modifier_referentiel(
    referentiel_id: UUID,
    requete: ModificationReferentielRequete,
    cas_usage: ModifierReferentiel = Depends(obtenir_cas_usage_modifier_referentiel),
) -> ReferentielReponse:
    """Modifie un référentiel existant."""
    try:
        referentiel = cas_usage.executer(
            CommandeModifierReferentiel(
                referentiel_id=referentiel_id,
                nom=requete.nom,
                description=requete.description,
                actif_par_defaut=requete.actif_par_defaut,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return ReferentielReponse.depuis_entite(referentiel)


@routeur.delete("/{referentiel_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_referentiel(
    referentiel_id: UUID,
    cas_usage: SupprimerReferentiel = Depends(obtenir_cas_usage_supprimer_referentiel),
) -> None:
    """Supprime définitivement un référentiel (et ses sections/questions)."""
    try:
        cas_usage.executer(referentiel_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur


@routeur.post(
    "/{referentiel_id}/sections", response_model=SectionReponse, status_code=status.HTTP_201_CREATED
)
def creer_section(
    referentiel_id: UUID,
    requete: CreationSectionRequete,
    cas_usage: CreerSectionReferentiel = Depends(obtenir_cas_usage_creer_section),
) -> SectionReponse:
    """Crée une nouvelle section dans un référentiel."""
    try:
        section = cas_usage.executer(
            CommandeCreerSection(referentiel_id=referentiel_id, nom=requete.nom)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return SectionReponse.depuis_entite(section)


@routeur.patch("/{referentiel_id}/sections/ordre", response_model=list[SectionReponse])
def reordonner_sections(
    referentiel_id: UUID,
    requete: ReordonnerSectionsRequete,
    cas_usage: ReordonnerSectionsReferentiel = Depends(obtenir_cas_usage_reordonner_sections),
) -> list[SectionReponse]:
    """Applique un nouvel ordre d'affichage aux sections d'un référentiel."""
    try:
        sections = cas_usage.executer(
            CommandeReordonnerSections(referentiel_id=referentiel_id, ids_ordonnes=requete.ids_ordonnes)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except ErreurValidationDomaine as erreur:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erreur)) from erreur
    return [SectionReponse.depuis_entite(section) for section in sections]
