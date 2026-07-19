"""Port (interface) pour la persistance des Sections de référentiel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.section_referentiel import SectionReferentiel


class SectionReferentielRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des sections."""

    @abstractmethod
    def ajouter(self, section: SectionReferentiel) -> None:
        """Persiste une nouvelle section."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, section_id: UUID) -> SectionReferentiel | None:
        """Retourne la section correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_referentiel(self, referentiel_id: UUID) -> list[SectionReferentiel]:
        """Retourne les sections d'un référentiel, triées par ordre puis nom."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, section: SectionReferentiel) -> None:
        """Enregistre les modifications apportées à une section existante."""
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, section_id: UUID) -> None:
        """Supprime définitivement une section (et ses questions)."""
        raise NotImplementedError

    @abstractmethod
    def compter_par_referentiel(self) -> dict[UUID, int]:
        """Retourne, pour chaque référentiel ayant au moins une section, son nombre de sections.

        Une seule requête agrégée pour tous les référentiels (pas de N+1).
        """
        raise NotImplementedError
