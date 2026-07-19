"""Entités métier de Mauricette (aucune dépendance vers l'infrastructure)."""

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import FournisseurStockage, StatutAppelOffre, StatutDocument

__all__ = [
    "AppelOffre",
    "Document",
    "FournisseurStockage",
    "StatutAppelOffre",
    "StatutDocument",
]
