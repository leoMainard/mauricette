"""Cas d'usage : réordonnancement des questions d'une section de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurValidationDomaine
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeReordonnerQuestions:
    """Données nécessaires au réordonnancement des questions d'une section."""

    section_id: UUID
    ids_ordonnes: list[UUID]


class ReordonnerQuestionsReferentiel:
    """Applique un nouvel ordre d'affichage aux questions d'une section."""

    def __init__(self, depot: QuestionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeReordonnerQuestions) -> list[QuestionReferentiel]:
        """Persiste le nouvel ordre, après vérification que la liste soumise correspond
        exactement aux questions existantes (ni id manquant, ni id étranger, ni doublon)."""
        existantes = self._depot.lister_par_section(commande.section_id)
        if not existantes:
            raise EntiteIntrouvable(
                f"Section introuvable ou sans question : {commande.section_id}"
            )

        soumis = commande.ids_ordonnes
        if len(soumis) != len(set(soumis)):
            raise ErreurValidationDomaine("La liste d'ordre contient des identifiants en double.")
        if set(soumis) != {question.id for question in existantes}:
            raise ErreurValidationDomaine(
                "La liste soumise ne correspond pas exactement aux questions existantes."
            )

        par_id = {question.id: question for question in existantes}
        for index, question_id in enumerate(soumis):
            par_id[question_id].ordre = index
            self._depot.mettre_a_jour(par_id[question_id])
        return [par_id[question_id] for question_id in soumis]
