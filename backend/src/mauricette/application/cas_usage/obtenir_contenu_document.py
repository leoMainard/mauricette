"""Cas d'usage : consultation du contenu binaire d'un document (aperçu dans l'interface)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


@dataclass(frozen=True)
class CommandeObtenirContenuDocument:
    """Données nécessaires à la consultation du contenu d'un document."""

    appel_offre_id: UUID
    document_id: UUID


@dataclass(frozen=True)
class ContenuDocument:
    """Octets bruts d'un document, avec les métadonnées nécessaires à la réponse HTTP."""

    contenu: bytes
    type_mime: str
    nom_original: str


class ObtenirContenuDocument:
    """Récupère le contenu binaire d'un document, pour aperçu dans l'interface."""

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._stockage = stockage

    def executer(self, commande: CommandeObtenirContenuDocument) -> ContenuDocument:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le document n'existe pas
        ou n'appartient pas à l'Appel d'Offres indiqué."""
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None or document.appel_offre_id != commande.appel_offre_id:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        contenu = self._stockage.recuperer(document.cle_stockage)
        return ContenuDocument(
            contenu=contenu,
            type_mime=document.type_mime,
            nom_original=document.nom_original,
        )
