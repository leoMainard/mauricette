"""Point d'entrée de l'API FastAPI de Mauricette."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mauricette.api.dependances import obtenir_utilisateur_courant
from mauricette.api.routes import (
    routeur_appel_offre_referentiels,
    routeur_appels_offre,
    routeur_auth,
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
    routeur_utilisateurs,
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

# `routeur_auth` n'est volontairement PAS protégé : c'est lui qui permet de s'authentifier.
app.include_router(routeur_auth, prefix="/api")

# Tous les autres routeurs exigent une session valide (protection globale, un seul
# endroit à maintenir plutôt qu'une dépendance ajoutée route par route).
_DEPENDANCE_AUTH = [Depends(obtenir_utilisateur_courant)]

app.include_router(routeur_appels_offre, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_documents, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_export, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_appel_offre_referentiels, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_referentiels, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_sections_referentiel, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_questions_referentiel, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_traitement_rag, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_reponses, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_chatbot, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_feedback, prefix="/api", dependencies=_DEPENDANCE_AUTH)
app.include_router(routeur_statistiques, prefix="/api", dependencies=_DEPENDANCE_AUTH)
# `routeur_utilisateurs` (administration) protège déjà chacune de ses routes par le
# statut ADMIN ; on ajoute quand même l'exigence de connexion pour rester cohérent
# avec le reste de l'API (401 avant même de vérifier le rôle si pas connecté).
app.include_router(routeur_utilisateurs, prefix="/api", dependencies=_DEPENDANCE_AUTH)


@app.get("/api/sante", tags=["Technique"])
def verifier_sante() -> dict[str, str]:
    """Endpoint de vérification de disponibilité de l'API."""
    return {"statut": "ok"}
