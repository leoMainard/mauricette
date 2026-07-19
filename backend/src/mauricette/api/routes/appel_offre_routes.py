"""Routes HTTP relatives aux Appels d'Offres."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_creer_appel_offre,
    obtenir_cas_usage_lister_appels_offre,
    obtenir_cas_usage_obtenir_appel_offre,
)
from mauricette.api.schemas.appel_offre_schemas import (
    AppelOffreDetailReponse,
    AppelOffreReponse,
    CreationAppelOffreRequete,
)
from mauricette.application.cas_usage.creer_appel_offre import (
    CommandeCreerAppelOffre,
    CreerAppelOffre,
)
from mauricette.application.cas_usage.lister_appels_offre import ListerAppelsOffre
from mauricette.application.cas_usage.obtenir_appel_offre import ObtenirAppelOffre
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/appels-offre", tags=["Appels d'Offres"])


@routeur.post("", response_model=AppelOffreReponse, status_code=status.HTTP_201_CREATED)
def creer_appel_offre(
    requete: CreationAppelOffreRequete,
    cas_usage: CreerAppelOffre = Depends(obtenir_cas_usage_creer_appel_offre),
) -> AppelOffreReponse:
    """Crée un nouvel Appel d'Offres."""
    appel_offre = cas_usage.executer(
        CommandeCreerAppelOffre(nom=requete.nom, cree_par=requete.cree_par)
    )
    return AppelOffreReponse.depuis_entite(appel_offre)


@routeur.get("", response_model=list[AppelOffreReponse])
def lister_appels_offre(
    cas_usage: ListerAppelsOffre = Depends(obtenir_cas_usage_lister_appels_offre),
) -> list[AppelOffreReponse]:
    """Liste tous les Appels d'Offres, du plus récent au plus ancien."""
    return [AppelOffreReponse.depuis_entite(ao) for ao in cas_usage.executer()]


@routeur.get("/{appel_offre_id}", response_model=AppelOffreDetailReponse)
def obtenir_appel_offre(
    appel_offre_id: UUID,
    cas_usage: ObtenirAppelOffre = Depends(obtenir_cas_usage_obtenir_appel_offre),
) -> AppelOffreDetailReponse:
    """Retourne le détail d'un Appel d'Offres et la liste de ses documents."""
    try:
        detail = cas_usage.executer(appel_offre_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return AppelOffreDetailReponse.depuis_detail(detail)
