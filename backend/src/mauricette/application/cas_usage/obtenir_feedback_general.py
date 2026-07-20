"""Cas d'usage : consultation du feedback général d'un AO."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.feedback_general_repository import FeedbackGeneralRepositoryPort


class ObtenirFeedbackGeneral:
    """Retourne le feedback général d'un AO, s'il en existe un."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_feedback: FeedbackGeneralRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_feedback = depot_feedback

    def executer(self, appel_offre_id: UUID) -> FeedbackGeneral | None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {appel_offre_id}")
        return self._depot_feedback.obtenir_par_appel_offre(appel_offre_id)
