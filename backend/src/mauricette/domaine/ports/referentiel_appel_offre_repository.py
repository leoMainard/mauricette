"""Port (interface) pour le rattachement des Référentiels aux Appels d'Offres.

Cette relation many-to-many mérite son propre port : ni le Référentiel ni
l'Appel d'Offres n'en est le seul propriétaire, c'est une association à part
entière (avec sa propre date de rattachement).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel


class ReferentielAppelOffreRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance de ce rattachement."""

    @abstractmethod
    def attacher(self, appel_offre_id: UUID, referentiel_id: UUID) -> None:
        """Rattache un référentiel à un Appel d'Offres (idempotent : pas d'erreur si déjà attaché)."""
        raise NotImplementedError

    @abstractmethod
    def detacher(self, appel_offre_id: UUID, referentiel_id: UUID) -> None:
        """Retire le rattachement d'un référentiel à un Appel d'Offres."""
        raise NotImplementedError

    @abstractmethod
    def lister_referentiels_pour_ao(self, appel_offre_id: UUID) -> list[Referentiel]:
        """Retourne les référentiels actuellement rattachés à un Appel d'Offres."""
        raise NotImplementedError

    @abstractmethod
    def compter_ao_par_referentiel(self) -> dict[UUID, int]:
        """Retourne, pour chaque référentiel, le nombre d'Appels d'Offres concernés.

        Une seule requête agrégée pour tous les référentiels (pas de N+1).
        """
        raise NotImplementedError

    @abstractmethod
    def compter_questions_actives_par_ao(self) -> dict[UUID, int]:
        """Retourne, pour chaque AO, le nombre de questions actives parmi ses référentiels attachés.

        Une seule requête agrégée (jointure appel_offre_referentiel → section_referentiel
        → question_referentiel), pas de N+1. Utilisé pour la barre de progression
        d'analyse dans la liste des AO.
        """
        raise NotImplementedError
