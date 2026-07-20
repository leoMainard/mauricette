"""Cas d'usage : consultation de l'état du pipeline RAG des documents d'un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)


class ObtenirEtatTraitementAppelOffre:
    """Retourne le suivi de traitement RAG de tous les documents d'un Appel d'Offres."""

    def __init__(self, depot_traitement_rag: DocumentTraitementRagRepositoryPort) -> None:
        self._depot_traitement_rag = depot_traitement_rag

    def executer(self, appel_offre_id: UUID) -> list[DocumentTraitementRag]:
        return self._depot_traitement_rag.lister_par_appel_offre(appel_offre_id)
