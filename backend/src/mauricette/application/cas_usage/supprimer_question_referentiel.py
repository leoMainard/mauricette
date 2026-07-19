"""Cas d'usage : suppression définitive d'une question de référentiel."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)


class SupprimerQuestionReferentiel:
    """Supprime définitivement une question du référentiel."""

    def __init__(self, depot: QuestionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, question_id: UUID) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si la question n'existe pas."""
        if self._depot.obtenir_par_id(question_id) is None:
            raise EntiteIntrouvable(f"Question introuvable : {question_id}")
        self._depot.supprimer(question_id)
