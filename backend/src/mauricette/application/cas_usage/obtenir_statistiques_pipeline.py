"""Cas d'usage : statistiques globales du pipeline RAG (tous AO confondus), pour le
tableau de bord admin."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.config.parametres import Parametres
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class StatistiquesPipeline:
    """Vue agrégée de la santé du pipeline RAG et de la file d'attente de traitement."""

    documents_par_etape: dict[str, dict[str, int]]
    taches_par_type: dict[str, dict[str, int]]
    taches_echecs_definitifs: int
    duree_moyenne_traitement_secondes: float | None


class ObtenirStatistiquesPipeline:
    """Assemble les statistiques globales du pipeline RAG (extraction/découpage/embedding)
    et de la file d'attente de traitement asynchrone."""

    def __init__(
        self,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        parametres: Parametres,
    ) -> None:
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_taches = depot_taches
        self._max_tentatives = parametres.rag_nombre_max_tentatives_tache

    def executer(self) -> StatistiquesPipeline:
        return StatistiquesPipeline(
            documents_par_etape=self._depot_traitement_rag.compter_par_etape_et_statut(),
            taches_par_type=self._depot_taches.compter_par_type_et_statut(),
            taches_echecs_definitifs=self._depot_taches.compter_echecs_definitifs(self._max_tentatives),
            duree_moyenne_traitement_secondes=self._depot_traitement_rag.duree_moyenne_traitement_secondes(),
        )
