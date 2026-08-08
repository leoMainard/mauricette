"""Routes HTTP du tableau de bord admin : vue globale de l'application (tous
utilisateurs confondus). Toutes les routes exigent le statut ADMIN."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from mauricette.api.dependances import (
    obtenir_cas_usage_lister_appels_offre,
    obtenir_cas_usage_lister_referentiels,
    obtenir_cas_usage_obtenir_statistiques_feedback,
    obtenir_cas_usage_obtenir_statistiques_pipeline,
    obtenir_cas_usage_obtenir_statistiques_qualite,
    obtenir_utilisateur_admin,
)
from mauricette.api.schemas.appel_offre_schemas import AppelOffreAvecStatistiquesReponse
from mauricette.api.schemas.feedback_schemas import StatistiquesFeedbackReponse
from mauricette.api.schemas.referentiel_schemas import ReferentielAvecStatistiquesReponse
from mauricette.api.schemas.statistiques_schemas import (
    StatistiquesPipelineReponse,
    StatistiquesQualiteReponse,
)
from mauricette.application.cas_usage.lister_appels_offre import ListerAppelsOffre
from mauricette.application.cas_usage.lister_referentiels import ListerReferentiels
from mauricette.application.cas_usage.obtenir_statistiques_feedback import (
    ObtenirStatistiquesFeedback,
)
from mauricette.application.cas_usage.obtenir_statistiques_pipeline import (
    ObtenirStatistiquesPipeline,
)
from mauricette.application.cas_usage.obtenir_statistiques_qualite import (
    ObtenirStatistiquesQualite,
)

routeur = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(obtenir_utilisateur_admin)],
)


@routeur.get("/appels-offre", response_model=list[AppelOffreAvecStatistiquesReponse])
def lister_tous_les_appels_offre(
    cas_usage: ListerAppelsOffre = Depends(obtenir_cas_usage_lister_appels_offre),
) -> list[AppelOffreAvecStatistiquesReponse]:
    """Liste TOUS les Appels d'Offres de l'application, sans filtre de visibilité
    (contrairement à `GET /appels-offre`, scopé à l'utilisateur/son groupe)."""
    return [
        AppelOffreAvecStatistiquesReponse.depuis_dto(dto)
        for dto in cas_usage.executer(terme_recherche=None, ids_proprietaires_visibles=None)
    ]


@routeur.get("/referentiels", response_model=list[ReferentielAvecStatistiquesReponse])
def lister_tous_les_referentiels(
    cas_usage: ListerReferentiels = Depends(obtenir_cas_usage_lister_referentiels),
) -> list[ReferentielAvecStatistiquesReponse]:
    """Liste TOUS les référentiels de l'application, sans filtre de visibilité."""
    return [
        ReferentielAvecStatistiquesReponse.depuis_dto(dto)
        for dto in cas_usage.executer(terme_recherche=None, ids_proprietaires_visibles=None)
    ]


@routeur.get("/feedback", response_model=StatistiquesFeedbackReponse)
def obtenir_statistiques_feedback(
    cas_usage: ObtenirStatistiquesFeedback = Depends(obtenir_cas_usage_obtenir_statistiques_feedback),
) -> StatistiquesFeedbackReponse:
    """Retourne les statistiques globales de feedback (tous AO confondus)."""
    return StatistiquesFeedbackReponse.depuis_dto(cas_usage.executer())


@routeur.get("/pipeline", response_model=StatistiquesPipelineReponse)
def obtenir_statistiques_pipeline(
    cas_usage: ObtenirStatistiquesPipeline = Depends(obtenir_cas_usage_obtenir_statistiques_pipeline),
) -> StatistiquesPipelineReponse:
    """Retourne les statistiques globales du pipeline RAG et de la file d'attente."""
    return StatistiquesPipelineReponse.depuis_dto(cas_usage.executer())


@routeur.get("/qualite", response_model=StatistiquesQualiteReponse)
def obtenir_statistiques_qualite(
    cas_usage: ObtenirStatistiquesQualite = Depends(obtenir_cas_usage_obtenir_statistiques_qualite),
) -> StatistiquesQualiteReponse:
    """Retourne les statistiques globales de qualité des réponses IA."""
    return StatistiquesQualiteReponse.depuis_dto(cas_usage.executer())
