"""Cas d'usage : détacher un référentiel d'un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.declencher_regeneration_reponses import (
    declencher_regeneration_reponses,
)
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeDetacherReferentiel:
    """Données nécessaires pour détacher un référentiel d'un Appel d'Offres."""

    appel_offre_id: UUID
    referentiel_id: UUID


class DetacherReferentielDeAppelOffre:
    """Retire le rattachement d'un référentiel à un Appel d'Offres."""

    def __init__(
        self,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
    ) -> None:
        self._depot_referentiels_ao = depot_referentiels_ao
        self._depot_appels_offre = depot_appels_offre
        self._depot_taches = depot_taches

    def executer(self, commande: CommandeDetacherReferentiel) -> None:
        """Exécute le cas d'usage (idempotent : pas d'erreur si déjà détaché)."""
        self._depot_referentiels_ao.detacher(commande.appel_offre_id, commande.referentiel_id)

        # Les questions du référentiel détaché ne doivent plus apparaître parmi
        # les réponses de l'AO : une régénération complète les élimine.
        declencher_regeneration_reponses(commande.appel_offre_id, self._depot_appels_offre, self._depot_taches)
