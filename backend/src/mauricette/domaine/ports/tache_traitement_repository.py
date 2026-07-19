"""Port (interface) pour la file d'attente des tâches de traitement asynchrone RAG."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.entites.tache_traitement import TacheTraitement


class TacheTraitementRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de file d'attente de traitement."""

    @abstractmethod
    def enqueuer(self, type_tache: TypeTache, reference_id: UUID) -> TacheTraitement:
        """Ajoute une nouvelle tâche à traiter par le worker."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_en_cours_ou_en_attente(
        self, type_tache: TypeTache, reference_id: UUID
    ) -> TacheTraitement | None:
        """Retourne une tâche déjà en file (EN_ATTENTE ou EN_COURS) pour ce type/cette référence.

        Utilisé pour éviter d'empiler plusieurs régénérations de réponses si
        plusieurs documents du même AO terminent leur embedding en rafale.
        """
        raise NotImplementedError

    @abstractmethod
    def reclamer_tache_suivante(self, types_geres: list[TypeTache]) -> TacheTraitement | None:
        """Réserve atomiquement la prochaine tâche éligible (`EN_ATTENTE`, échéance passée).

        Implémentation attendue via un verrou `SELECT ... FOR UPDATE SKIP LOCKED`
        pour permettre plusieurs workers concurrents sans double-traitement.
        Retourne None si aucune tâche n'est disponible.
        """
        raise NotImplementedError

    @abstractmethod
    def marquer_reussie(self, tache_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def remettre_en_attente(self, tache_id: UUID, message_erreur: str, delai_secondes: int) -> None:
        """Erreur transitoire : remet la tâche en file, éligible après `delai_secondes`."""
        raise NotImplementedError

    @abstractmethod
    def marquer_echouee(self, tache_id: UUID, message_erreur: str) -> None:
        """Erreur définitive (ou nombre max de tentatives dépassé) : la tâche ne sera plus retentée."""
        raise NotImplementedError
