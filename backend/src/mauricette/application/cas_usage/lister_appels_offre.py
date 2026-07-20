"""Cas d'usage : lister les Appels d'Offres existants, avec recherche et statistiques."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.enums import StatutAppelOffre, TypeTache
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort, StatistiquesDocuments
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort

STATISTIQUES_VIDES = StatistiquesDocuments(nombre_documents=0, taille_totale_octets=0)


@dataclass(frozen=True)
class AppelOffreAvecStatistiques:
    """Un Appel d'Offres accompagné du nombre et du poids total de ses documents."""

    appel_offre: AppelOffre
    statistiques: StatistiquesDocuments
    en_erreur_analyse: bool


class ListerAppelsOffre:
    """Retourne la liste des Appels d'Offres, du plus récent au plus ancien.

    Filtre par nom si un terme de recherche est fourni. Enrichit chaque AO avec
    ses statistiques de documents et son état d'erreur d'analyse, chacun en une
    seule requête agrégée (pas de N+1).
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents
        self._depot_taches = depot_taches

    def executer(self, terme_recherche: str | None = None) -> list[AppelOffreAvecStatistiques]:
        """Exécute le cas d'usage."""
        appels_offre = self._depot_appels_offre.lister_tous(terme_recherche)
        statistiques_par_ao = self._depot_documents.compter_par_appel_offre()
        ao_ids_en_erreur = self._depot_taches.lister_reference_ids_en_echec(
            TypeTache.REGENERATION_REPONSES_AO
        )

        return [
            AppelOffreAvecStatistiques(
                appel_offre=appel_offre,
                statistiques=statistiques_par_ao.get(appel_offre.id, STATISTIQUES_VIDES),
                en_erreur_analyse=appel_offre.statut == StatutAppelOffre.EN_COURS
                and appel_offre.id in ao_ids_en_erreur,
            )
            for appel_offre in appels_offre
        ]
