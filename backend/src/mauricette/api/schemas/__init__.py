"""Schémas Pydantic (contrats HTTP) exposés par l'API."""

from mauricette.api.schemas.appel_offre_schemas import (
    AppelOffreAvecStatistiquesReponse,
    AppelOffreDetailReponse,
    AppelOffreReponse,
    CreationAppelOffreRequete,
    ModificationAppelOffreRequete,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse, DocumentReponse

__all__ = [
    "AppelOffreAvecStatistiquesReponse",
    "AppelOffreDetailReponse",
    "AppelOffreReponse",
    "CreationAppelOffreRequete",
    "DepotFichierReponse",
    "DocumentReponse",
    "ModificationAppelOffreRequete",
]
