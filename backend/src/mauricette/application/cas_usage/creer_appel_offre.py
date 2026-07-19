"""Cas d'usage : création d'un nouvel Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort


@dataclass(frozen=True)
class CommandeCreerAppelOffre:
    """Données nécessaires à la création d'un Appel d'Offres."""

    nom: str
    cree_par: str


class CreerAppelOffre:
    """Orchestre la création et la persistance d'un nouvel Appel d'Offres."""

    def __init__(self, depot_appels_offre: AppelOffreRepositoryPort) -> None:
        self._depot_appels_offre = depot_appels_offre

    def executer(self, commande: CommandeCreerAppelOffre) -> AppelOffre:
        """Crée l'Appel d'Offres et le persiste via le repository."""
        appel_offre = AppelOffre(nom=commande.nom, cree_par=commande.cree_par)
        self._depot_appels_offre.ajouter(appel_offre)
        return appel_offre
