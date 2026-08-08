"""Schémas Pydantic (contrats HTTP) pour les statistiques globales du tableau de bord."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from mauricette.application.cas_usage.obtenir_statistiques_pipeline import StatistiquesPipeline
from mauricette.application.cas_usage.obtenir_statistiques_qualite import StatistiquesQualite


class VolumeJourReponse(BaseModel):
    """Nombre de documents traités durant un jour donné."""

    jour: date
    nombre: int


class StatistiquesPipelineReponse(BaseModel):
    """Statistiques globales du pipeline RAG et de la file d'attente de traitement,
    pour le tableau de bord admin."""

    documents_par_etape: dict[str, dict[str, int]]
    taches_par_type: dict[str, dict[str, int]]
    taches_echecs_definitifs: int
    duree_moyenne_traitement_secondes: float | None

    @classmethod
    def depuis_dto(cls, dto: StatistiquesPipeline) -> "StatistiquesPipelineReponse":
        return cls(
            documents_par_etape=dto.documents_par_etape,
            taches_par_type=dto.taches_par_type,
            taches_echecs_definitifs=dto.taches_echecs_definitifs,
            duree_moyenne_traitement_secondes=dto.duree_moyenne_traitement_secondes,
        )


class StatistiquesQualiteReponse(BaseModel):
    """Statistiques globales de qualité des réponses IA, pour le tableau de bord admin."""

    total_reponses: int
    reponses_par_statut: dict[str, int]
    scores_confiance: list[float]
    sans_contenu_par_referentiel: dict[UUID, dict[str, int]]

    @classmethod
    def depuis_dto(cls, dto: StatistiquesQualite) -> "StatistiquesQualiteReponse":
        return cls(
            total_reponses=dto.total_reponses,
            reponses_par_statut=dto.reponses_par_statut,
            scores_confiance=dto.scores_confiance,
            sans_contenu_par_referentiel=dto.sans_contenu_par_referentiel,
        )
