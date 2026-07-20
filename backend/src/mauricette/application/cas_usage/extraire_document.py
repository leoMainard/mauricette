"""Cas d'usage : extraction du contenu structuré d'un document (1ère étape du pipeline RAG)."""

from __future__ import annotations

import io
from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.serialisation_extraction import (
    TYPE_MIME_EXTRACTION,
    cle_stockage_extraction,
    serialiser_resultat_extraction,
)
from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurTraitementDefinitive, ErreurTraitementTransitoire
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.extracteur_document import ExtracteurDocumentPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeExtraireDocument:
    """Identifie le document dont il faut extraire le contenu."""

    document_id: UUID


class ExtraireDocument:
    """Extrait le contenu structuré d'un document et enchaîne sur l'étape de découpage.

    Le résultat d'extraction est stocké en JSON (via `StockageDocumentPort`) plutôt
    qu'en base : c'est un artefact intermédiaire volumineux, pas une donnée à
    interroger, et cette réutilisation évite de gonfler Postgres.
    """

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        stockage: StockageDocumentPort,
        extracteur: ExtracteurDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_taches = depot_taches
        self._stockage = stockage
        self._extracteur = extracteur

    def executer(self, commande: CommandeExtraireDocument) -> None:
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        traitement = self._depot_traitement_rag.obtenir(commande.document_id)
        if traitement is None:
            raise EntiteIntrouvable(
                f"Suivi de traitement RAG introuvable pour le document : {commande.document_id}"
            )

        traitement.demarrer_extraction()
        self._depot_traitement_rag.mettre_a_jour(traitement)

        try:
            contenu = self._stockage.recuperer(document.cle_stockage)
            resultat = self._extracteur.extraire(contenu, document.nom_original, document.type_mime)
            self._stockage.enregistrer(
                cle_stockage_extraction(document.appel_offre_id, document.id),
                io.BytesIO(serialiser_resultat_extraction(resultat)),
                TYPE_MIME_EXTRACTION,
            )
        except (ErreurTraitementDefinitive, ErreurTraitementTransitoire) as erreur:
            traitement.echouer_extraction(str(erreur))
            self._depot_traitement_rag.mettre_a_jour(traitement)
            raise

        traitement.reussir_extraction()
        self._depot_traitement_rag.mettre_a_jour(traitement)
        self._depot_taches.enqueuer(TypeTache.DECOUPAGE_DOCUMENT, document.id)
