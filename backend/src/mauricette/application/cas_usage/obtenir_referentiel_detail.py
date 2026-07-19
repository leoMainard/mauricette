"""Cas d'usage : consulter le détail complet d'un référentiel (sections + questions)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class SectionAvecQuestions:
    """Une section accompagnée de ses questions."""

    section: SectionReferentiel
    questions: list[QuestionReferentiel]


@dataclass(frozen=True)
class DetailReferentiel:
    """Vue complète d'un référentiel : ses sections (avec leurs questions) et ses statistiques."""

    referentiel: Referentiel
    sections: list[SectionAvecQuestions]
    nombre_ao_concernes: int


class ObtenirReferentielDetail:
    """Récupère un référentiel avec l'intégralité de ses sections et questions."""

    def __init__(
        self,
        depot_referentiels: ReferentielRepositoryPort,
        depot_sections: SectionReferentielRepositoryPort,
        depot_questions: QuestionReferentielRepositoryPort,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
    ) -> None:
        self._depot_referentiels = depot_referentiels
        self._depot_sections = depot_sections
        self._depot_questions = depot_questions
        self._depot_referentiels_ao = depot_referentiels_ao

    def executer(self, referentiel_id: UUID) -> DetailReferentiel:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le référentiel n'existe pas."""
        referentiel = self._depot_referentiels.obtenir_par_id(referentiel_id)
        if referentiel is None:
            raise EntiteIntrouvable(f"Référentiel introuvable : {referentiel_id}")

        sections = self._depot_sections.lister_par_referentiel(referentiel_id)
        toutes_questions = self._depot_questions.lister_par_referentiel(referentiel_id)

        questions_par_section: dict[UUID, list[QuestionReferentiel]] = {}
        for question in toutes_questions:
            questions_par_section.setdefault(question.section_id, []).append(question)

        sections_avec_questions = [
            SectionAvecQuestions(section=section, questions=questions_par_section.get(section.id, []))
            for section in sections
        ]

        nombre_ao_concernes = self._depot_referentiels_ao.compter_ao_par_referentiel().get(
            referentiel_id, 0
        )

        return DetailReferentiel(
            referentiel=referentiel,
            sections=sections_avec_questions,
            nombre_ao_concernes=nombre_ao_concernes,
        )
