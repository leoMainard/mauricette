"""Cas d'usage : lister les Appels d'Offres existants."""

from __future__ import annotations

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort


class ListerAppelsOffre:
    """Retourne la liste des Appels d'Offres, du plus récent au plus ancien."""

    def __init__(self, depot_appels_offre: AppelOffreRepositoryPort) -> None:
        self._depot_appels_offre = depot_appels_offre

    def executer(self) -> list[AppelOffre]:
        """Exécute le cas d'usage."""
        return self._depot_appels_offre.lister_tous()
