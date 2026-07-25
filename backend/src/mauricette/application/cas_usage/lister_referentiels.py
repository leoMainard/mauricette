"""Cas d'usage : lister les référentiels existants, avec recherche et statistiques."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel
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
class ReferentielAvecStatistiques:
    """Un référentiel accompagné de ses statistiques d'utilisation."""

    referentiel: Referentiel
    nombre_sections: int
    nombre_questions_actives: int
    nombre_ao_concernes: int


class ListerReferentiels:
    """Retourne les référentiels, triés par nom, enrichis de leurs statistiques.

    Chaque statistique est calculée en une seule requête agrégée par dépôt
    (pas de N+1), puis assemblée en mémoire pour chaque référentiel.
    """

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

    def executer(
        self,
        terme_recherche: str | None = None,
        ids_proprietaires_visibles: list[UUID] | None = None,
    ) -> list[ReferentielAvecStatistiques]:
        """Exécute le cas d'usage."""
        referentiels = self._depot_referentiels.lister_tous(
            terme_recherche, ids_proprietaires_visibles
        )
        nb_sections = self._depot_sections.compter_par_referentiel()
        nb_questions = self._depot_questions.compter_actives_par_referentiel()
        nb_ao = self._depot_referentiels_ao.compter_ao_par_referentiel()

        return [
            ReferentielAvecStatistiques(
                referentiel=referentiel,
                nombre_sections=nb_sections.get(referentiel.id, 0),
                nombre_questions_actives=nb_questions.get(referentiel.id, 0),
                nombre_ao_concernes=nb_ao.get(referentiel.id, 0),
            )
            for referentiel in referentiels
        ]
