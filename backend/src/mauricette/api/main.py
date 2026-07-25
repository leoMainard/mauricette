"""Point d'entrée de l'API FastAPI de Mauricette."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mauricette.api.routes import (
    routeur_appel_offre_referentiels,
    routeur_appels_offre,
    routeur_chatbot,
    routeur_documents,
    routeur_export,
    routeur_feedback,
    routeur_questions_referentiel,
    routeur_referentiels,
    routeur_reponses,
    routeur_sections_referentiel,
    routeur_statistiques,
    routeur_traitement_rag,
)
from mauricette.config.parametres import obtenir_parametres

parametres = obtenir_parametres()

app = FastAPI(
    title="Mauricette",
    description="Assistant IA pour l'analyse des documents d'Appels d'Offres.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parametres.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routeur_appels_offre, prefix="/api")
app.include_router(routeur_documents, prefix="/api")
app.include_router(routeur_export, prefix="/api")
app.include_router(routeur_appel_offre_referentiels, prefix="/api")
app.include_router(routeur_referentiels, prefix="/api")
app.include_router(routeur_sections_referentiel, prefix="/api")
app.include_router(routeur_questions_referentiel, prefix="/api")
app.include_router(routeur_traitement_rag, prefix="/api")
app.include_router(routeur_reponses, prefix="/api")
app.include_router(routeur_chatbot, prefix="/api")
app.include_router(routeur_feedback, prefix="/api")
app.include_router(routeur_statistiques, prefix="/api")


@app.get("/api/sante", tags=["Technique"])
def verifier_sante() -> dict[str, str]:
    """Endpoint de vérification de disponibilité de l'API."""
    return {"statut": "ok"}
