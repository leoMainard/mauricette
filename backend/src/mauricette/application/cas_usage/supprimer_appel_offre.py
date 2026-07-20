"""Cas d'usage : suppression complète d'un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


class SupprimerAppelOffre:
    """Supprime un Appel d'Offres et tout ce qui en dépend.

    Les documents sont d'abord effacés du stockage un par un (le stockage
    n'étant pas nettoyé par la contrainte `ON DELETE CASCADE`, contrairement
    aux lignes en base : documents, chunks, tâches et réponses liées à l'AO
    disparaissent automatiquement à la suppression de la ligne `appel_offre`).
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents
        self._stockage = stockage

    def executer(self, appel_offre_id: UUID) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {appel_offre_id}")

        for document in self._depot_documents.lister_par_appel_offre(appel_offre_id):
            self._stockage.supprimer(document.cle_stockage)

        self._depot_appels_offre.supprimer(appel_offre_id)
