"""Cas d'usage : rattacher un référentiel à un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.declencher_regeneration_reponses import (
    declencher_regeneration_reponses,
)
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeAttacherReferentiel:
    """Données nécessaires au rattachement d'un référentiel à un Appel d'Offres."""

    appel_offre_id: UUID
    referentiel_id: UUID


class AttacherReferentielAAppelOffre:
    """Rattache manuellement un référentiel supplémentaire à un Appel d'Offres."""

    def __init__(
        self,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_referentiels: ReferentielRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
    ) -> None:
        self._depot_referentiels_ao = depot_referentiels_ao
        self._depot_appels_offre = depot_appels_offre
        self._depot_referentiels = depot_referentiels
        self._depot_taches = depot_taches

    def executer(self, commande: CommandeAttacherReferentiel) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO ou le référentiel n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")
        if self._depot_referentiels.obtenir_par_id(commande.referentiel_id) is None:
            raise EntiteIntrouvable(f"Référentiel introuvable : {commande.referentiel_id}")

        self._depot_referentiels_ao.attacher(commande.appel_offre_id, commande.referentiel_id)

        # Le référentiel attaché peut apporter de nouvelles questions actives :
        # les réponses de l'AO doivent être recalculées pour les couvrir.
        declencher_regeneration_reponses(commande.appel_offre_id, self._depot_appels_offre, self._depot_taches)
