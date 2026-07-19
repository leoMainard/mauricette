"""Cas d'usage : consultation des réponses générées pour un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.reponse_question import ReponseQuestion
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort


class ListerReponsesAppelOffre:
    """Retourne toutes les réponses générées pour un Appel d'Offres."""

    def __init__(self, depot_reponses: ReponseQuestionRepositoryPort) -> None:
        self._depot_reponses = depot_reponses

    def executer(self, appel_offre_id: UUID) -> list[ReponseQuestion]:
        return self._depot_reponses.lister_par_appel_offre(appel_offre_id)
