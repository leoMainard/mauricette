"""Cas d'usage : création d'une nouvelle question dans une section de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeCreerQuestionReferentiel:
    """Données nécessaires à la création d'une question."""

    section_id: UUID
    question: str
    format_reponse: FormatReponse
    aide_extraction: str | None = None
    obligatoire: bool = False


class CreerQuestionReferentiel:
    """Orchestre la création et la persistance d'une nouvelle question."""

    def __init__(
        self,
        depot_questions: QuestionReferentielRepositoryPort,
        depot_sections: SectionReferentielRepositoryPort,
    ) -> None:
        self._depot_questions = depot_questions
        self._depot_sections = depot_sections

    def executer(self, commande: CommandeCreerQuestionReferentiel) -> QuestionReferentiel:
        """Crée la question et la persiste, après vérification que la section existe."""
        if self._depot_sections.obtenir_par_id(commande.section_id) is None:
            raise EntiteIntrouvable(f"Section introuvable : {commande.section_id}")

        questions_existantes = self._depot_questions.lister_par_section(commande.section_id)
        question = QuestionReferentiel(
            section_id=commande.section_id,
            question=commande.question,
            format_reponse=commande.format_reponse,
            aide_extraction=commande.aide_extraction,
            obligatoire=commande.obligatoire,
            ordre=len(questions_existantes),
        )
        self._depot_questions.ajouter(question)
        return question
