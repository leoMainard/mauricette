"""Entité métier : fragment de texte (ou tableau) extrait d'un document, destiné à l'embedding."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import TypeChunk
from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class Chunk:
    """Fragment de contenu d'un document, unité de base de la recherche RAG.

    `appel_offre_id` est dénormalisé depuis le document parent : la recherche
    de chunks se fait toujours à l'échelle d'un AO (jamais entre AO), et cette
    dénormalisation évite une jointure sur `document` à chaque requête.
    """

    document_id: UUID
    appel_offre_id: UUID
    contenu: str
    type_chunk: TypeChunk
    id: UUID = field(default_factory=uuid4)
    page_debut: int | None = None
    page_fin: int | None = None
    titre_section: str | None = None
    ordre: int = 0
    embedding: list[float] | None = None
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.contenu or not self.contenu.strip():
            raise ErreurValidationDomaine("Le contenu d'un chunk ne peut pas être vide.")
        if self.ordre < 0:
            raise ErreurValidationDomaine("L'ordre d'un chunk ne peut pas être négatif.")

    def assigner_embedding(self, vecteur: list[float]) -> None:
        """Associe le vecteur d'embedding calculé pour ce chunk."""
        self.embedding = vecteur
