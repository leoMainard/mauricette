"""Port (interface) pour le découpage d'un document extrait en chunks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.chunk import Chunk
from mauricette.domaine.ports.extracteur_document import ResultatExtraction


class DecoupeurDocumentPort(ABC):
    """Contrat que doit respecter tout adaptateur de découpage en chunks.

    Un adaptateur de découpage est pur : il ne persiste rien, il construit
    seulement les `Chunk` à partir du résultat d'extraction.
    """

    @abstractmethod
    def decouper(
        self, document_id: UUID, appel_offre_id: UUID, resultat_extraction: ResultatExtraction
    ) -> list[Chunk]:
        """Découpe le résultat d'extraction en chunks prêts à être vectorisés et stockés."""
        raise NotImplementedError
