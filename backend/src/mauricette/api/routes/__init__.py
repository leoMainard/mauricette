"""Routeurs FastAPI, regroupés par ressource métier."""

from mauricette.api.routes.appel_offre_routes import routeur as routeur_appels_offre
from mauricette.api.routes.document_routes import routeur as routeur_documents

__all__ = ["routeur_appels_offre", "routeur_documents"]
