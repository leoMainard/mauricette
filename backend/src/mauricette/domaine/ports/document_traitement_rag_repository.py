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

    @abstractmethod
    def compter_par_etape_et_statut(self) -> dict[str, dict[str, int]]:
        """Retourne, pour chaque étape du pipeline (extraction/decoupage/embedding), le
        nombre de documents dans chaque statut, tous AO confondus. Trois requêtes
        agrégées (une par étape), pas de N+1."""
        raise NotImplementedError

    @abstractmethod
    def duree_moyenne_traitement_secondes(self) -> float | None:
        """Durée moyenne (en secondes) entre la création du suivi et la réussite de
        l'embedding, pour les documents dont le pipeline est allé à son terme. `None`
        si aucun document n'a encore terminé."""
        raise NotImplementedError
