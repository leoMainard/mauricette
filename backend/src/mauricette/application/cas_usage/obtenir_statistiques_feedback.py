"""Cas d'usage : statistiques globales de feedback (tous AO confondus), pour le
tableau de bord admin."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.ports.feedback_general_repository import FeedbackGeneralRepositoryPort
from mauricette.domaine.ports.feedback_reponse_repository import (
    FeedbackReponseDetaille,
    FeedbackReponseRepositoryPort,
)


@dataclass(frozen=True)
class StatistiquesFeedback:
    """Vue agrégée des feedbacks général et par réponse, tous AO confondus."""

    general_par_avis: dict[str, int]
    reponse_par_avis: dict[str, int]
    reponse_par_type_erreur: dict[str, int]
    general_bruts: list[FeedbackGeneral]
    reponse_negatifs_par_referentiel: dict[UUID, int]
    reponse_detailles: list[FeedbackReponseDetaille]


class ObtenirStatistiquesFeedback:
    """Assemble les statistiques de feedback globales de l'application."""

    def __init__(
        self,
        depot_feedback_general: FeedbackGeneralRepositoryPort,
        depot_feedback_reponse: FeedbackReponseRepositoryPort,
    ) -> None:
        self._depot_feedback_general = depot_feedback_general
        self._depot_feedback_reponse = depot_feedback_reponse

    def executer(self) -> StatistiquesFeedback:
        return StatistiquesFeedback(
            general_par_avis=self._depot_feedback_general.compter_par_avis(),
            reponse_par_avis=self._depot_feedback_reponse.compter_par_avis(),
            reponse_par_type_erreur=self._depot_feedback_reponse.compter_par_type_erreur(),
            general_bruts=self._depot_feedback_general.lister_tous(),
            reponse_negatifs_par_referentiel=self._depot_feedback_reponse.compter_negatifs_par_referentiel(),
            reponse_detailles=self._depot_feedback_reponse.lister_tous_avec_contexte(),
        )
