"""Port (interface) pour la persistance des Appels d'Offres.

N'importe quel adaptateur (PostgreSQL, autre SGBD, mémoire pour les tests...)
peut implémenter ce port. Le domaine et l'application ne connaissent que cette
interface, jamais l'implémentation concrète.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre


class AppelOffreRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des AO."""

    @abstractmethod
    def ajouter(self, appel_offre: AppelOffre) -> None:
        """Persiste un nouvel Appel d'Offres."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, appel_offre_id: UUID) -> AppelOffre | None:
        """Retourne l'AO correspondant à l'identifiant, ou None s'il n'existe pas."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous(self, terme_recherche: str | None = None) -> list[AppelOffre]:
        """Retourne les Appels d'Offres, triés du plus récent au plus ancien.

        Si `terme_recherche` est fourni, ne retourne que les AO dont le nom le
        contient (recherche insensible à la casse).
        """
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, appel_offre: AppelOffre) -> None:
        """Enregistre les modifications apportées à un Appel d'Offres existant."""
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, appel_offre_id: UUID) -> None:
        """Supprime définitivement un Appel d'Offres et tout ce qui en dépend (cascade en base)."""
        raise NotImplementedError
