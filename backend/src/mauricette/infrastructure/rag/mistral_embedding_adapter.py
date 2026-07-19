"""Adaptateur d'embedding basé sur l'API Mistral (modèle `mistral-embed`)."""

from __future__ import annotations

from mistralai.client import Mistral
from mistralai.client.errors.mistralerror import MistralError

from mauricette.config.parametres import Parametres
from mauricette.domaine.exceptions import ErreurEmbeddingIndisponible
from mauricette.domaine.ports.embedding import EmbeddingPort

DIMENSION_MISTRAL_EMBED = 1024


class MistralEmbeddingAdapter(EmbeddingPort):
    """Vectorise du texte via l'API Mistral."""

    def __init__(self, parametres: Parametres) -> None:
        self._client = Mistral(api_key=parametres.mistral_api_key)
        self._modele = parametres.mistral_embed_model
        self._taille_lot = parametres.rag_taille_lot_embedding

    @property
    def dimension(self) -> int:
        return DIMENSION_MISTRAL_EMBED

    def vectoriser_lot(self, textes: list[str]) -> list[list[float]]:
        if not textes:
            return []
        vecteurs: list[list[float]] = []
        for debut in range(0, len(textes), self._taille_lot):
            lot = textes[debut : debut + self._taille_lot]
            try:
                reponse = self._client.embeddings.create(model=self._modele, inputs=lot)
            except MistralError as erreur:
                raise ErreurEmbeddingIndisponible(
                    f"Le service d'embedding Mistral est indisponible : {erreur}"
                ) from erreur
            except Exception as erreur:  # timeout réseau, DNS, etc.
                raise ErreurEmbeddingIndisponible(
                    f"Échec de connexion au service d'embedding Mistral : {erreur}"
                ) from erreur
            vecteurs.extend(donnee.embedding for donnee in reponse.data)
        return vecteurs

    def vectoriser_un(self, texte: str) -> list[float]:
        return self.vectoriser_lot([texte])[0]
