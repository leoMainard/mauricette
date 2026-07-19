"""Port (interface) pour la persistance du suivi de traitement RAG d'un document."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag


class DocumentTraitementRagRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance du suivi de traitement RAG."""

    @abstractmethod
    def creer(self, document_id: UUID, appel_offre_id: UUID) -> DocumentTraitementRag:
        """Initialise le suivi de traitement d'un document nouvellement déposé."""
        raise NotImplementedError

    @abstractmethod
    def obtenir(self, document_id: UUID) -> DocumentTraitementRag | None:
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, entite: DocumentTraitementRag) -> None:
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[DocumentTraitementRag]:
        raise NotImplementedError
