"""Routes HTTP relatives aux statistiques globales du tableau de bord."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from mauricette.api.dependances import obtenir_cas_usage_obtenir_volume_documents_par_jour
from mauricette.api.schemas.statistiques_schemas import VolumeJourReponse
from mauricette.application.cas_usage.obtenir_volume_documents_par_jour import (
    ObtenirVolumeDocumentsParJour,
)

routeur = APIRouter(prefix="/statistiques", tags=["Statistiques"])


@routeur.get("/documents-par-jour", response_model=list[VolumeJourReponse])
def obtenir_volume_documents_par_jour(
    cas_usage: ObtenirVolumeDocumentsParJour = Depends(
        obtenir_cas_usage_obtenir_volume_documents_par_jour
    ),
) -> list[VolumeJourReponse]:
    """Retourne le volume de documents dont l'analyse s'est terminée, par jour."""
    volumes = cas_usage.executer()
    return [
        VolumeJourReponse(jour=jour, nombre=nombre) for jour, nombre in sorted(volumes.items())
    ]
