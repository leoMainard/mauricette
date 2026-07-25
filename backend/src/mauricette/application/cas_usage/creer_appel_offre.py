"""Cas d'usage : création d'un nouvel Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort


@dataclass(frozen=True)
class CommandeCreerAppelOffre:
    """Données nécessaires à la création d'un Appel d'Offres."""

    nom: str
    cree_par: str
    cree_par_id: UUID


class CreerAppelOffre:
    """Orchestre la création et la persistance d'un nouvel Appel d'Offres.

    Les référentiels marqués "actifs par défaut" sont automatiquement rattachés
    au nouvel AO ; l'utilisateur pourra toujours en rattacher d'autres ensuite.
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_referentiels: ReferentielRepositoryPort,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_referentiels = depot_referentiels
        self._depot_referentiels_ao = depot_referentiels_ao

    def executer(self, commande: CommandeCreerAppelOffre) -> AppelOffre:
        """Crée l'Appel d'Offres, le persiste, puis y rattache les référentiels par défaut."""
        appel_offre = AppelOffre(
            nom=commande.nom, cree_par=commande.cree_par, cree_par_id=commande.cree_par_id
        )
        self._depot_appels_offre.ajouter(appel_offre)

        for referentiel in self._depot_referentiels.lister_actifs_par_defaut():
            self._depot_referentiels_ao.attacher(appel_offre.id, referentiel.id)

        return appel_offre
