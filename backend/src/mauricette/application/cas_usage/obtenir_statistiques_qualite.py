"""Cas d'usage : statistiques globales de qualité des réponses IA (tous AO confondus),
pour le tableau de bord admin."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort


@dataclass(frozen=True)
class StatistiquesQualite:
    """Vue agrégée de la qualité des réponses générées par le RAG."""

    total_reponses: int
    reponses_par_statut: dict[str, int]
    scores_confiance: list[float]
    sans_contenu_par_referentiel: dict[UUID, dict[str, int]]


class ObtenirStatistiquesQualite:
    """Assemble les statistiques globales de qualité des réponses (confiance, taux de
    réponses trouvées, taux de validation, référentiels les plus problématiques)."""

    def __init__(self, depot_reponses: ReponseQuestionRepositoryPort) -> None:
        self._depot_reponses = depot_reponses

    def executer(self) -> StatistiquesQualite:
        return StatistiquesQualite(
            total_reponses=self._depot_reponses.compter_total(),
            reponses_par_statut=self._depot_reponses.compter_par_statut(),
            scores_confiance=self._depot_reponses.lister_scores_confiance(),
            sans_contenu_par_referentiel=self._depot_reponses.compter_sans_contenu_par_referentiel(),
        )
