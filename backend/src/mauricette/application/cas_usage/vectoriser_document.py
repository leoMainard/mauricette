"""Cas d'usage : calcul des embeddings des chunks d'un document (3ème et dernière étape du pipeline RAG)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.cas_usage.declencher_regeneration_reponses import (
    declencher_regeneration_reponses,
)
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurTraitementDefinitive, ErreurTraitementTransitoire
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.embedding import EmbeddingPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeVectoriserDocument:
    """Identifie le document dont il faut vectoriser les chunks."""

    document_id: UUID


class VectoriserDocument:
    """Calcule et persiste les embeddings des chunks d'un document.

    Une fois l'embedding réussi, déclenche la régénération complète des réponses
    de l'AO (le corpus de documents indexés a changé). Une garde évite d'empiler
    plusieurs régénérations si plusieurs documents du même AO terminent en rafale.
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_chunks: ChunkRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        embedding: EmbeddingPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_chunks = depot_chunks
        self._depot_taches = depot_taches
        self._embedding = embedding

    def executer(self, commande: CommandeVectoriserDocument) -> None:
        document = self._depot_documents.obtenir_par_id(commande.document_id)
        if document is None:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        traitement = self._depot_traitement_rag.obtenir(commande.document_id)
        if traitement is None:
            raise EntiteIntrouvable(
                f"Suivi de traitement RAG introuvable pour le document : {commande.document_id}"
            )

        traitement.demarrer_embedding()
        self._depot_traitement_rag.mettre_a_jour(traitement)

        try:
            chunks = self._depot_chunks.lister_sans_embedding(document.id)
            if chunks:
                vecteurs = self._embedding.vectoriser_lot([chunk.contenu for chunk in chunks])
                self._depot_chunks.mettre_a_jour_embeddings(
                    {chunk.id: vecteur for chunk, vecteur in zip(chunks, vecteurs, strict=True)}
                )
        except (ErreurTraitementDefinitive, ErreurTraitementTransitoire) as erreur:
            traitement.echouer_embedding(str(erreur))
            self._depot_traitement_rag.mettre_a_jour(traitement)
            raise

        traitement.reussir_embedding()
        self._depot_traitement_rag.mettre_a_jour(traitement)

        declencher_regeneration_reponses(document.appel_offre_id, self._depot_appels_offre, self._depot_taches)
