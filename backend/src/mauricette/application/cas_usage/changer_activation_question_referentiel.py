"""Cas d'usage : archiver ou réactiver une question de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeChangerActivationQuestion:
    """Données nécessaires pour archiver ou réactiver une question."""

    question_id: UUID
    actif: bool


class ChangerActivationQuestionReferentiel:
    """Archive (masque) ou réactive une question sans la supprimer."""

    def __init__(self, depot: QuestionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeChangerActivationQuestion) -> QuestionReferentiel:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si la question n'existe pas."""
        question = self._depot.obtenir_par_id(commande.question_id)
        if question is None:
            raise EntiteIntrouvable(f"Question introuvable : {commande.question_id}")

        if commande.actif:
            question.reactiver()
        else:
            question.archiver()

        self._depot.mettre_a_jour(question)
        return question
