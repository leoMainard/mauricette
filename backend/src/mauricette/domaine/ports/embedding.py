"""Port (interface) pour la vectorisation (embedding) de texte.

Permet de changer de fournisseur d'embedding (Mistral, Voyage AI, OpenAI...)
en ne modifiant qu'un adaptateur dans `infrastructure/rag/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """Contrat que doit respecter tout adaptateur de vectorisation de texte."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimension des vecteurs produits par ce fournisseur (ex: 1024 pour mistral-embed)."""
        raise NotImplementedError

    @abstractmethod
    def vectoriser_lot(self, textes: list[str]) -> list[list[float]]:
        """Vectorise un lot de textes, dans l'ordre fourni.

        Lève `ErreurEmbeddingIndisponible` (transitoire) en cas de quota atteint
        ou de timeout réseau.
        """
        raise NotImplementedError

    @abstractmethod
    def vectoriser_un(self, texte: str) -> list[float]:
        """Vectorise un unique texte (utilisé notamment pour vectoriser une requête)."""
        raise NotImplementedError
