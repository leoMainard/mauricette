"""Port (interface) pour le stockage binaire des documents.

C'est le port qui permet de changer de fournisseur de stockage (disque local,
MinIO, Cloudflare R2, AWS S3...) en ne modifiant qu'un adaptateur dans
`infrastructure/stockage/`, sans toucher au domaine, aux cas d'usage ni à l'API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO

from mauricette.domaine.entites.enums import FournisseurStockage


class StockageDocumentPort(ABC):
    """Contrat que doit respecter tout adaptateur de stockage de documents."""

    @property
    @abstractmethod
    def fournisseur(self) -> FournisseurStockage:
        """Identifiant du fournisseur, stocké sur le document pour traçabilité."""
        raise NotImplementedError

    @abstractmethod
    def enregistrer(self, cle: str, contenu: BinaryIO, type_mime: str) -> None:
        """Écrit le contenu binaire sous la clé donnée.

        Args:
            cle: identifiant unique du fichier dans l'espace de stockage
                (ex: "ao/<id_ao>/<id_document>_<nom_fichier>").
            contenu: flux binaire du fichier à enregistrer.
            type_mime: type MIME du fichier (ex: "application/pdf").
        """
        raise NotImplementedError

    @abstractmethod
    def recuperer(self, cle: str) -> bytes:
        """Retourne le contenu binaire du fichier associé à la clé."""
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, cle: str) -> None:
        """Supprime le fichier associé à la clé, si présent."""
        raise NotImplementedError

    @abstractmethod
    def generer_url_temporaire(self, cle: str, expiration_secondes: int = 3600) -> str:
        """Retourne une URL permettant de télécharger le fichier temporairement."""
        raise NotImplementedError
