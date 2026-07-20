"""Port (interface) pour la persistance du feedback sur les réponses générées."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.feedback_reponse import FeedbackReponse


class FeedbackReponseRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance du feedback par réponse."""

    @abstractmethod
    def enregistrer(self, feedback: FeedbackReponse) -> FeedbackReponse:
        """Crée ou remplace (upsert par `(appel_offre_id, question_referentiel_id)`)."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[FeedbackReponse]:
        """Une seule requête agrégée pour tous les feedbacks de l'AO (pas de N+1),
        utilisée pour préremplir l'état des pouces à l'ouverture de l'onglet Questions.
        """
        raise NotImplementedError
