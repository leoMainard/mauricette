"""Ports (interfaces) du domaine, à implémenter par la couche infrastructure."""

from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort

__all__ = [
    "AppelOffreRepositoryPort",
    "DocumentRepositoryPort",
    "StockageDocumentPort",
]
