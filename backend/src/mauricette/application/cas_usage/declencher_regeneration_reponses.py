"""Déclenchement partagé d'une régénération des réponses d'un AO.

Utilisé par tout cas d'usage modifiant le corpus documentaire ou les questions
posées (dépôt/suppression de document, rattachement/détachement de référentiel) :
centralise la garde anti-doublon et la réouverture douce de l'AO.
"""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.enums import StatutAppelOffre, TypeTache
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


def declencher_regeneration_reponses(
    appel_offre_id: UUID,
    depot_appels_offre: AppelOffreRepositoryPort,
    depot_taches: TacheTraitementRepositoryPort,
) -> None:
    """Enfile une régénération des réponses de l'AO, et le rouvre s'il était déjà traité.

    Réouverture douce : un AO "traité" repasse en "en cours" pour signaler qu'un
    retraitement est en route, jamais l'inverse (un AO en brouillon ou archivé
    n'est pas affecté).
    """
    appel_offre = depot_appels_offre.obtenir_par_id(appel_offre_id)
    if appel_offre is not None and appel_offre.statut == StatutAppelOffre.TRAITE:
        appel_offre.passer_en_cours()
        depot_appels_offre.mettre_a_jour(appel_offre)

    tache_existante = depot_taches.obtenir_en_cours_ou_en_attente(
        TypeTache.REGENERATION_REPONSES_AO, appel_offre_id
    )
    if tache_existante is None:
        depot_taches.enqueuer(TypeTache.REGENERATION_REPONSES_AO, appel_offre_id)
