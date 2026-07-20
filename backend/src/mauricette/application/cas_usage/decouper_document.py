"""Cas d'usage : découpage en chunks du résultat d'extraction (2ème étape du pipeline RAG)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.serialisation_extraction import (
    cle_stockage_extraction,
    deserialiser_resultat_extraction,
)
from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurTraitementDefinitive, ErreurTraitementTransitoire
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.decoupeur_document import DecoupeurDocumentPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeDecouperDocument:
    """Identifie le document dont il faut découper le résultat d'extraction."""

    document_id: UUID


class DecouperDocument:
    """Découpe en chunks le résultat d'extraction d'un document, puis enchaîne sur l'embedding."""

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_chunks: ChunkRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        stockage: StockageDocumentPort,
        decoupeur: DecoupeurDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_chunks = depot_chunks
        self._depot_taches = depot_taches
        self._stockage = stockage
        self._decoupeur = decoupeur

    def executer(self, commande: CommandeDecouperDocument) -> None:
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        traitement = self._depot_traitement_rag.obtenir(commande.document_id)
        if traitement is None:
            raise EntiteIntrouvable(
                f"Suivi de traitement RAG introuvable pour le document : {commande.document_id}"
            )

        traitement.demarrer_decoupage()
        self._depot_traitement_rag.mettre_a_jour(traitement)

        try:
            contenu_extraction = self._stockage.recuperer(
                cle_stockage_extraction(document.appel_offre_id, document.id)
            )
            resultat_extraction = deserialiser_resultat_extraction(contenu_extraction)
            chunks = self._decoupeur.decouper(document.id, document.appel_offre_id, resultat_extraction)
            self._depot_chunks.remplacer_pour_document(document.id, chunks)
        except (ErreurTraitementDefinitive, ErreurTraitementTransitoire) as erreur:
            traitement.echouer_decoupage(str(erreur))
            self._depot_traitement_rag.mettre_a_jour(traitement)
            raise

        traitement.reussir_decoupage()
        self._depot_traitement_rag.mettre_a_jour(traitement)
        self._depot_taches.enqueuer(TypeTache.EMBEDDING_DOCUMENT, document.id)
