"""Cas d'usage : relance manuelle de l'analyse (régénération des réponses) d'un AO."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.declencher_regeneration_reponses import (
    declencher_regeneration_reponses,
)
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeReanalyserAppelOffre:
    """Identifie l'Appel d'Offres dont il faut relancer l'analyse."""

    appel_offre_id: UUID


class ReanalyserAppelOffre:
    """Déclenche manuellement une régénération complète des réponses d'un AO.

    Utile quand l'utilisateur veut forcer un nouveau calcul sans attendre un
    dépôt/suppression de document (ex: après une modification du référentiel).
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_taches = depot_taches

    def executer(self, commande: CommandeReanalyserAppelOffre) -> None:
        if self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        declencher_regeneration_reponses(commande.appel_offre_id, self._depot_appels_offre, self._depot_taches)
