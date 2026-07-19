"""Port (interface) pour la persistance des Référentiels."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel


class ReferentielRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des référentiels."""

    @abstractmethod
    def ajouter(self, referentiel: Referentiel) -> None:
        """Persiste un nouveau référentiel."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, referentiel_id: UUID) -> Referentiel | None:
        """Retourne le référentiel correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous(self, terme_recherche: str | None = None) -> list[Referentiel]:
        """Retourne les référentiels, triés par nom.

        Si `terme_recherche` est fourni, ne retourne que ceux dont le nom le contient.
        """
        raise NotImplementedError

    @abstractmethod
    def lister_actifs_par_defaut(self) -> list[Referentiel]:
        """Retourne les référentiels marqués comme actifs par défaut.

        Utilisé pour les rattacher automatiquement à un nouvel Appel d'Offres.
        """
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, referentiel: Referentiel) -> None:
        """Enregistre les modifications apportées à un référentiel existant."""
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, referentiel_id: UUID) -> None:
        """Supprime définitivement un référentiel (et ses sections/questions)."""
        raise NotImplementedError
