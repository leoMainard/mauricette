"""Cas d'usage : lister les Appels d'Offres existants, avec recherche et statistiques."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort, StatistiquesDocuments

STATISTIQUES_VIDES = StatistiquesDocuments(nombre_documents=0, taille_totale_octets=0)


@dataclass(frozen=True)
class AppelOffreAvecStatistiques:
    """Un Appel d'Offres accompagné du nombre et du poids total de ses documents."""

    appel_offre: AppelOffre
    statistiques: StatistiquesDocuments


class ListerAppelsOffre:
    """Retourne la liste des Appels d'Offres, du plus récent au plus ancien.

    Filtre par nom si un terme de recherche est fourni. Enrichit chaque AO avec
    ses statistiques de documents en une seule requête agrégée (pas de N+1).
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents

    def executer(self, terme_recherche: str | None = None) -> list[AppelOffreAvecStatistiques]:
        """Exécute le cas d'usage."""
        appels_offre = self._depot_appels_offre.lister_tous(terme_recherche)
        statistiques_par_ao = self._depot_documents.compter_par_appel_offre()

        return [
            AppelOffreAvecStatistiques(
                appel_offre=appel_offre,
                statistiques=statistiques_par_ao.get(appel_offre.id, STATISTIQUES_VIDES),
            )
            for appel_offre in appels_offre
        ]
