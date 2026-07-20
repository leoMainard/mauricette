"""Routeurs FastAPI, regroupés par ressource métier."""

from mauricette.api.routes.appel_offre_referentiel_routes import (
    routeur as routeur_appel_offre_referentiels,
)
from mauricette.api.routes.appel_offre_routes import routeur as routeur_appels_offre
from mauricette.api.routes.chatbot_routes import routeur as routeur_chatbot
from mauricette.api.routes.document_routes import routeur as routeur_documents
from mauricette.api.routes.feedback_routes import routeur as routeur_feedback
from mauricette.api.routes.question_referentiel_routes import (
    routeur as routeur_questions_referentiel,
)
from mauricette.api.routes.referentiel_routes import routeur as routeur_referentiels
from mauricette.api.routes.section_referentiel_routes import (
    routeur as routeur_sections_referentiel,
)
from mauricette.api.routes.statistiques_routes import routeur as routeur_statistiques
from mauricette.api.routes.traitement_rag_routes import routeur as routeur_traitement_rag
from mauricette.api.routes.traitement_rag_routes import routeur_reponses

__all__ = [
    "routeur_appel_offre_referentiels",
    "routeur_appels_offre",
    "routeur_chatbot",
    "routeur_documents",
    "routeur_feedback",
    "routeur_questions_referentiel",
    "routeur_referentiels",
    "routeur_reponses",
    "routeur_sections_referentiel",
    "routeur_statistiques",
    "routeur_traitement_rag",
]
