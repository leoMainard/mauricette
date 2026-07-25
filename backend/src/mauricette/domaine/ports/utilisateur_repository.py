"""Port (interface) pour la persistance des Utilisateurs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.utilisateur import Utilisateur


class UtilisateurRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des utilisateurs."""

    @abstractmethod
    def ajouter(self, utilisateur: Utilisateur) -> None:
        """Persiste un nouvel utilisateur."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, utilisateur_id: UUID) -> Utilisateur | None:
        """Retourne l'utilisateur correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_email(self, email: str) -> Utilisateur | None:
        """Retourne l'utilisateur correspondant à l'email (insensible à la casse), ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous(self) -> list[Utilisateur]:
        """Retourne tous les utilisateurs, triés par nom (usage : administration)."""
        raise NotImplementedError

    @abstractmethod
    def lister_ids_par_groupe(self, groupe_id: UUID) -> list[UUID]:
        """Retourne les identifiants de tous les utilisateurs membres d'un groupe."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, utilisateur: Utilisateur) -> None:
        """Enregistre les modifications apportées à un utilisateur existant."""
        raise NotImplementedError
