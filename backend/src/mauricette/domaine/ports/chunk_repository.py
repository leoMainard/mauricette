"""Port (interface) pour la persistance des chunks issus du découpage des documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.chunk import Chunk

# Nombre de chunks retournés par défaut par une recherche hybride, si l'appelant
# n'en précise pas explicitement (voir `parametres.rag_nombre_chunks_recherche`).
LIMITE_RECHERCHE_PAR_DEFAUT = 8


class ChunkRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des chunks."""

    @abstractmethod
    def remplacer_pour_document(self, document_id: UUID, chunks: list[Chunk]) -> None:
        """Supprime les chunks existants d'un document puis insère les nouveaux.

        Idempotent par construction : réutilisé aussi bien pour le découpage
        initial que pour une relance après échec (avec `chunks=[]` pour ne
        faire que la purge).
        """
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour_embeddings(self, embeddings_par_chunk_id: dict[UUID, list[float]]) -> None:
        """Associe à chaque chunk (par id) son vecteur d'embedding calculé."""
        raise NotImplementedError

    @abstractmethod
    def lister_sans_embedding(self, document_id: UUID) -> list[Chunk]:
        """Retourne les chunks d'un document dont l'embedding n'a pas encore été calculé."""
        raise NotImplementedError

    @abstractmethod
    def recherche_hybride(
        self,
        appel_offre_id: UUID,
        vecteur_question: list[float],
        texte_question: str,
        limite: int = LIMITE_RECHERCHE_PAR_DEFAUT,
    ) -> list[Chunk]:
        """Retourne les chunks les plus pertinents d'un AO pour une question donnée.

        Combine similarité vectorielle (embeddings) et recherche plein texte,
        toujours scopée à un seul AO — la recherche ne traverse jamais plusieurs AO.
        """
        raise NotImplementedError
