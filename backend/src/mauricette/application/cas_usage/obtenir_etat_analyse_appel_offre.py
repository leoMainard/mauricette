"""Cas d'usage : consultation de l'état de la dernière analyse (régénération) d'un AO."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.entites.tache_traitement import TacheTraitement
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


class ObtenirEtatAnalyseAppelOffre:
    """Retourne la dernière tâche de régénération des réponses d'un AO, si elle existe.

    Permet au client de distinguer un traitement toujours en cours d'un échec
    définitif : le statut de l'AO seul ("en cours") ne fait pas cette différence.
    """

    def __init__(self, depot_taches: TacheTraitementRepositoryPort) -> None:
        self._depot_taches = depot_taches

    def executer(self, appel_offre_id: UUID) -> TacheTraitement | None:
        return self._depot_taches.obtenir_derniere_tache(
            TypeTache.REGENERATION_REPONSES_AO, appel_offre_id
        )
