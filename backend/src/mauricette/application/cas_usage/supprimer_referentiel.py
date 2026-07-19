"""Cas d'usage : suppression définitive d'un référentiel."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort


class SupprimerReferentiel:
    """Supprime définitivement un référentiel (et, en cascade, ses sections et questions)."""

    def __init__(self, depot: ReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, referentiel_id: UUID) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le référentiel n'existe pas."""
        if self._depot.obtenir_par_id(referentiel_id) is None:
            raise EntiteIntrouvable(f"Référentiel introuvable : {referentiel_id}")
        self._depot.supprimer(referentiel_id)
