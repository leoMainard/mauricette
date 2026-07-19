"""Cas d'usage : lister les référentiels rattachés à un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)


class ListerReferentielsAppelOffre:
    """Retourne les référentiels actuellement rattachés à un Appel d'Offres."""

    def __init__(self, depot_referentiels_ao: ReferentielAppelOffreRepositoryPort) -> None:
        self._depot_referentiels_ao = depot_referentiels_ao

    def executer(self, appel_offre_id: UUID) -> list[Referentiel]:
        """Exécute le cas d'usage."""
        return self._depot_referentiels_ao.lister_referentiels_pour_ao(appel_offre_id)
