"""Port (interface) pour la persistance du feedback général d'un Appel d'Offres."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.feedback_general import FeedbackGeneral


class FeedbackGeneralRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance du feedback général."""

    @abstractmethod
    def enregistrer(self, feedback: FeedbackGeneral) -> FeedbackGeneral:
        """Crée ou remplace (upsert par `appel_offre_id`) le feedback général d'un AO."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_appel_offre(self, appel_offre_id: UUID) -> FeedbackGeneral | None:
        raise NotImplementedError
