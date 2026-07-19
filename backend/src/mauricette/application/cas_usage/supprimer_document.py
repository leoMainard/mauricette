"""Cas d'usage : suppression d'un document."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeSupprimerDocument:
    """Données nécessaires à la suppression d'un document."""

    appel_offre_id: UUID
    document_id: UUID


class SupprimerDocument:
    """Supprime un document : son contenu dans le stockage, puis son enregistrement.

    Les chunks associés sont nettoyés automatiquement par la contrainte
    `ON DELETE CASCADE` en base, sans code applicatif nécessaire. La disparition
    du document invalidant potentiellement les réponses déjà générées pour cet
    AO, une régénération complète est déclenchée dans la foulée.
    """

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._depot_taches = depot_taches
        self._stockage = stockage

    def executer(self, commande: CommandeSupprimerDocument) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le document n'existe pas
        ou n'appartient pas à l'Appel d'Offres indiqué."""
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None or document.appel_offre_id != commande.appel_offre_id:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        self._stockage.supprimer(document.cle_stockage)
        self._depot_documents.supprimer(document.id)

        tache_existante = self._depot_taches.obtenir_en_cours_ou_en_attente(
            TypeTache.REGENERATION_REPONSES_AO, document.appel_offre_id
        )
        if tache_existante is None:
            self._depot_taches.enqueuer(TypeTache.REGENERATION_REPONSES_AO, document.appel_offre_id)
