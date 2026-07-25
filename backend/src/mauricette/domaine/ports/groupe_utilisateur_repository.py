"""Port (interface) pour la persistance des Groupes d'utilisateurs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.groupe_utilisateur import GroupeUtilisateur


class GroupeUtilisateurRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des groupes d'utilisateurs."""

    @abstractmethod
    def ajouter(self, groupe: GroupeUtilisateur) -> None:
        """Persiste un nouveau groupe."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, groupe_id: UUID) -> GroupeUtilisateur | None:
        """Retourne le groupe correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous(self) -> list[GroupeUtilisateur]:
        """Retourne tous les groupes, triés par nom."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, groupe: GroupeUtilisateur) -> None:
        """Enregistre les modifications apportées à un groupe existant."""
        raise NotImplementedError
