"""Schémas Pydantic (contrats HTTP) exposés par l'API."""

from mauricette.api.schemas.appel_offre_schemas import (
    AppelOffreDetailReponse,
    AppelOffreReponse,
    CreationAppelOffreRequete,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse, DocumentReponse

__all__ = [
    "AppelOffreDetailReponse",
    "AppelOffreReponse",
    "CreationAppelOffreRequete",
    "DepotFichierReponse",
    "DocumentReponse",
]
