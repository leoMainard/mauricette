"""Cas d'usage : modification du contenu d'une question de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeModifierQuestionReferentiel:
    """Données nécessaires à la modification d'une question."""

    question_id: UUID
    question: str
    format_reponse: FormatReponse
    aide_extraction: str | None = None
    obligatoire: bool = False


class ModifierQuestionReferentiel:
    """Modifie le contenu d'une question existante."""

    def __init__(self, depot: QuestionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeModifierQuestionReferentiel) -> QuestionReferentiel:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si la question n'existe pas."""
        question = self._depot.obtenir_par_id(commande.question_id)
        if question is None:
            raise EntiteIntrouvable(f"Question introuvable : {commande.question_id}")

        question.modifier(
            question=commande.question,
            format_reponse=commande.format_reponse,
            aide_extraction=commande.aide_extraction,
            obligatoire=commande.obligatoire,
        )
        self._depot.mettre_a_jour(question)
        return question
