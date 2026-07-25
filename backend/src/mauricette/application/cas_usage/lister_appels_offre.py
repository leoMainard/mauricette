"""Cas d'usage : lister les Appels d'Offres existants, avec recherche et statistiques."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.enums import StatutAppelOffre, TypeTache
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort, StatistiquesDocuments
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort

STATISTIQUES_VIDES = StatistiquesDocuments(nombre_documents=0, taille_totale_octets=0)


@dataclass(frozen=True)
class AppelOffreAvecStatistiques:
    """Un Appel d'Offres accompagné du nombre et du poids total de ses documents."""

    appel_offre: AppelOffre
    statistiques: StatistiquesDocuments
    en_erreur_analyse: bool
    questions_actives: int
    reponses_generees: int


class ListerAppelsOffre:
    """Retourne la liste des Appels d'Offres, du plus récent au plus ancien.

    Filtre par nom si un terme de recherche est fourni. Enrichit chaque AO avec
    ses statistiques de documents, son état d'erreur d'analyse et son avancement
    d'analyse (questions actives / réponses renseignées), chacun en une seule
    requête agrégée (pas de N+1).
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
        depot_reponses: ReponseQuestionRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents
        self._depot_taches = depot_taches
        self._depot_referentiels_ao = depot_referentiels_ao
        self._depot_reponses = depot_reponses

    def executer(
        self,
        terme_recherche: str | None = None,
        ids_proprietaires_visibles: list[UUID] | None = None,
    ) -> list[AppelOffreAvecStatistiques]:
        """Exécute le cas d'usage."""
        appels_offre = self._depot_appels_offre.lister_tous(
            terme_recherche, ids_proprietaires_visibles
        )
        statistiques_par_ao = self._depot_documents.compter_par_appel_offre()
        ao_ids_en_erreur = self._depot_taches.lister_reference_ids_en_echec(
            TypeTache.REGENERATION_REPONSES_AO
        )
        questions_actives_par_ao = self._depot_referentiels_ao.compter_questions_actives_par_ao()
        reponses_generees_par_ao = self._depot_reponses.compter_avec_contenu_par_appel_offre()

        return [
            AppelOffreAvecStatistiques(
                appel_offre=appel_offre,
                statistiques=statistiques_par_ao.get(appel_offre.id, STATISTIQUES_VIDES),
                en_erreur_analyse=appel_offre.statut == StatutAppelOffre.EN_COURS
                and appel_offre.id in ao_ids_en_erreur,
                questions_actives=questions_actives_par_ao.get(appel_offre.id, 0),
                reponses_generees=reponses_generees_par_ao.get(appel_offre.id, 0),
            )
            for appel_offre in appels_offre
        ]
