"""Cas d'usage : relance du traitement RAG d'un document en échec."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import StatutEtape, TypeTache
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurEtatTraitementInvalide
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeRelancerDocument:
    """Identifie le document (rattaché à un AO) dont il faut relancer le traitement."""

    appel_offre_id: UUID
    document_id: UUID


class RelancerDocument:
    """Relance depuis le début le traitement RAG d'un document en échec.

    Repart systématiquement de l'extraction plutôt que de tenter de deviner
    quelle étape a échoué : c'est le choix le plus simple et le plus sûr, et le
    coût d'une extraction en trop est négligeable face à la fiabilité gagnée.
    """

    def __init__(
        self,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_chunks: ChunkRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
    ) -> None:
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_chunks = depot_chunks
        self._depot_taches = depot_taches

    def executer(self, commande: CommandeRelancerDocument) -> None:
        traitement = self._depot_traitement_rag.obtenir(commande.document_id)
        if traitement is None or traitement.appel_offre_id != commande.appel_offre_id:
            raise EntiteIntrouvable(f"Document introuvable : {commande.document_id}")

        if traitement.statut_global != StatutEtape.ECHEC:
            raise ErreurEtatTraitementInvalide(
                "Seul un document en échec de traitement peut être relancé."
            )

        self._depot_chunks.remplacer_pour_document(commande.document_id, [])
        traitement.reinitialiser()
        self._depot_traitement_rag.mettre_a_jour(traitement)
        self._depot_taches.enqueuer(TypeTache.EXTRACTION_DOCUMENT, commande.document_id)
