"""Port (interface) pour l'extraction de contenu structuré d'un document.

Permet de changer d'outil d'extraction (Docling, Azure Document Intelligence...)
en ne modifiant qu'un adaptateur dans `infrastructure/rag/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from mauricette.domaine.entites.enums import TypeChunk


@dataclass(frozen=True)
class ElementExtrait:
    """Un élément de contenu extrait d'un document (paragraphe, titre ou tableau)."""

    type_element: TypeChunk
    texte: str
    titre_section: str | None
    niveau_titre: int | None
    page_debut: int | None
    page_fin: int | None


@dataclass(frozen=True)
class ResultatExtraction:
    """Résultat complet de l'extraction d'un document, avant découpage en chunks."""

    elements: list[ElementExtrait]


class ExtracteurDocumentPort(ABC):
    """Contrat que doit respecter tout adaptateur d'extraction de documents."""

    @abstractmethod
    def extraire(self, contenu: bytes, nom_fichier: str, type_mime: str) -> ResultatExtraction:
        """Extrait le contenu structuré d'un document.

        Lève `ErreurExtractionDocument` (définitive) si le format n'est pas
        supporté, si le document est protégé par un mot de passe, ou si
        l'extraction échoue pour toute autre raison qu'une relance ne résoudra pas.
        """
        raise NotImplementedError
