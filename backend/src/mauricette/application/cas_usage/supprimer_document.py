"""Cas d'usage : suppression d'un document."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


@dataclass(frozen=True)
class CommandeSupprimerDocument:
    """Données nécessaires à la suppression d'un document."""

    appel_offre_id: UUID
    document_id: UUID


class SupprimerDocument:
    """Supprime un document : son contenu dans le stockage, puis son enregistrement."""

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._stockage = stockage

    def executer(self, commande: CommandeSupprimerDocument) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le document n'existe pas
        ou n'appartient pas à l'Appel d'Offres indiqué."""
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None or document.appel_offre_id != commande.appel_offre_id:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        self._stockage.supprimer(document.cle_stockage)
        self._depot_documents.supprimer(document.id)
