"""Cas d'usage : lister les feedbacks sur les réponses d'un AO."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.feedback_reponse import FeedbackReponse
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.feedback_reponse_repository import FeedbackReponseRepositoryPort


class ListerFeedbackReponses:
    """Retourne tous les feedbacks de réponses enregistrés pour un AO."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_feedback: FeedbackReponseRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_feedback = depot_feedback

    def executer(self, appel_offre_id: UUID) -> list[FeedbackReponse]:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {appel_offre_id}")
        return self._depot_feedback.lister_par_appel_offre(appel_offre_id)
