"""Cas d'usage : détacher un référentiel d'un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)


@dataclass(frozen=True)
class CommandeDetacherReferentiel:
    """Données nécessaires pour détacher un référentiel d'un Appel d'Offres."""

    appel_offre_id: UUID
    referentiel_id: UUID


class DetacherReferentielDeAppelOffre:
    """Retire le rattachement d'un référentiel à un Appel d'Offres."""

    def __init__(self, depot_referentiels_ao: ReferentielAppelOffreRepositoryPort) -> None:
        self._depot_referentiels_ao = depot_referentiels_ao

    def executer(self, commande: CommandeDetacherReferentiel) -> None:
        """Exécute le cas d'usage (idempotent : pas d'erreur si déjà détaché)."""
        self._depot_referentiels_ao.detacher(commande.appel_offre_id, commande.referentiel_id)
