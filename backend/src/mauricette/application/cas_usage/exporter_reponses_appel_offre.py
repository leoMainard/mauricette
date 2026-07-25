"""Cas d'usage : assemblage des données nécessaires à l'export du questionnaire d'un AO.

Ce cas d'usage ne produit qu'un modèle neutre (dataclasses simples), sans aucune
dépendance à une bibliothèque de rendu (PDF/DOCX/XLSX) : le rendu proprement dit
vit dans la couche API (`api/export/`), qui est la seule à connaître ces formats.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class ExportQuestion:
    """Une question et sa réponse, prêtes à être mises en forme."""

    question: str
    format_reponse: FormatReponse
    obligatoire: bool
    contenu: str | None
    citations: list[str]


@dataclass(frozen=True)
class ExportSection:
    """Une section et ses questions actives (celles réellement affichées à l'écran)."""

    nom: str
    questions: list[ExportQuestion]


@dataclass(frozen=True)
class ExportReferentiel:
    """Un référentiel et ses sections non vides."""

    nom: str
    sections: list[ExportSection]


@dataclass(frozen=True)
class ExportReponses:
    """Vue complète et neutre du questionnaire d'un AO, prête à être exportée."""

    nom_appel_offre: str
    referentiels: list[ExportReferentiel]


def _formater_citation(document_nom: str, page_debut: int | None) -> str:
    """Reprend le même format que l'affichage à l'écran (`OngletQuestions.tsx`) :
    nom de fichier court + page de départ si connue."""
    nom_court = posixpath.basename(document_nom.replace("\\", "/"))
    return f"{nom_court}, p.{page_debut}" if page_debut else nom_court


class ExporterReponsesAppelOffre:
    """Assemble le questionnaire complet (questions actives + réponses) d'un AO pour export."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
        depot_sections: SectionReferentielRepositoryPort,
        depot_questions: QuestionReferentielRepositoryPort,
        depot_reponses: ReponseQuestionRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_referentiels_ao = depot_referentiels_ao
        self._depot_sections = depot_sections
        self._depot_questions = depot_questions
        self._depot_reponses = depot_reponses

    def executer(self, appel_offre_id: UUID) -> ExportReponses:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'offres introuvable : {appel_offre_id}")

        reponses_par_question = {
            reponse.question_referentiel_id: reponse
            for reponse in self._depot_reponses.lister_par_appel_offre(appel_offre_id)
        }

        referentiels_attaches = self._depot_referentiels_ao.lister_referentiels_pour_ao(
            appel_offre_id
        )

        export_referentiels: list[ExportReferentiel] = []
        for referentiel in referentiels_attaches:
            sections = self._depot_sections.lister_par_referentiel(referentiel.id)
            toutes_questions = self._depot_questions.lister_par_referentiel(referentiel.id)
            questions_par_section: dict[UUID, list] = {}
            for question in toutes_questions:
                if question.actif:
                    questions_par_section.setdefault(question.section_id, []).append(question)

            export_sections: list[ExportSection] = []
            for section in sections:
                questions_actives = questions_par_section.get(section.id, [])
                if not questions_actives:
                    # Une section sans question active n'est jamais affichée à l'écran
                    # (voir OngletQuestions.tsx) : l'export doit refléter exactement la même vue.
                    continue

                export_questions = []
                for question in questions_actives:
                    reponse = reponses_par_question.get(question.id)
                    citations = (
                        [_formater_citation(c.document_nom, c.page_debut) for c in reponse.citations]
                        if reponse
                        else []
                    )
                    export_questions.append(
                        ExportQuestion(
                            question=question.question,
                            format_reponse=question.format_reponse,
                            obligatoire=question.obligatoire,
                            contenu=reponse.contenu if reponse else None,
                            citations=citations,
                        )
                    )
                export_sections.append(ExportSection(nom=section.nom, questions=export_questions))

            if export_sections:
                export_referentiels.append(
                    ExportReferentiel(nom=referentiel.nom, sections=export_sections)
                )

        return ExportReponses(nom_appel_offre=appel_offre.nom, referentiels=export_referentiels)
