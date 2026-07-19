"""Cas d'usage : modification du nom d'un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort


@dataclass(frozen=True)
class CommandeModifierAppelOffre:
    """Données nécessaires à la modification du nom d'un Appel d'Offres."""

    appel_offre_id: UUID
    nouveau_nom: str


class ModifierAppelOffre:
    """Renomme un Appel d'Offres existant."""

    def __init__(self, depot_appels_offre: AppelOffreRepositoryPort) -> None:
        self._depot_appels_offre = depot_appels_offre

    def executer(self, commande: CommandeModifierAppelOffre) -> AppelOffre:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        appel_offre.renommer(commande.nouveau_nom)
        self._depot_appels_offre.mettre_a_jour(appel_offre)
        return appel_offre
