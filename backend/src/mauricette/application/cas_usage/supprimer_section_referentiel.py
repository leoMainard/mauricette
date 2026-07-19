"""Cas d'usage : suppression d'une section de référentiel."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


class SupprimerSectionReferentiel:
    """Supprime définitivement une section (et, en cascade, ses questions)."""

    def __init__(self, depot: SectionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, section_id: UUID) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si la section n'existe pas."""
        if self._depot.obtenir_par_id(section_id) is None:
            raise EntiteIntrouvable(f"Section introuvable : {section_id}")
        self._depot.supprimer(section_id)
