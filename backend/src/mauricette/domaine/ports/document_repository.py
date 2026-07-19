"""Port (interface) pour la persistance des Documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.document import Document


class DocumentRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des documents."""

    @abstractmethod
    def ajouter(self, document: Document) -> None:
        """Persiste un nouveau document."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, document_id: UUID) -> Document | None:
        """Retourne le document correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[Document]:
        """Retourne tous les documents rattachés à un Appel d'Offres."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, document: Document) -> None:
        """Enregistre les modifications apportées à un document existant."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_hash(self, appel_offre_id: UUID, hash_sha256: str) -> Document | None:
        """Retourne un document existant du même AO ayant le même contenu (même hash), si présent.

        Utilisé pour détecter les doublons avant d'écrire un nouveau document.
        """
        raise NotImplementedError
