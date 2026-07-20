"""Port (interface) pour la génération de réponses à partir de chunks retrouvés.

Permet de changer de fournisseur de génération (Mistral, Anthropic Claude...)
en ne modifiant qu'un adaptateur dans `infrastructure/rag/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import FormatReponse, RoleMessageChatbot


@dataclass(frozen=True)
class ExtraitContexte:
    """Un chunk retrouvé, avec ses métadonnées, fourni en contexte à la génération."""

    chunk_id: UUID
    document_id: UUID
    document_nom: str
    page_debut: int | None
    page_fin: int | None
    titre_section: str | None
    contenu: str


@dataclass(frozen=True)
class ReponseGeneree:
    """Résultat de la génération : contenu, confiance, et chunks effectivement utilisés."""

    contenu: str | None
    score_confiance: float
    chunks_utilises: list[UUID]


@dataclass(frozen=True)
class TourConversation:
    """Un échange passé (question ou réponse), réinjecté comme contexte conversationnel.

    Utilisé par le chatbot pour permettre les questions de suivi ; absent pour la
    génération des réponses aux questions de référentiel (chacune est indépendante).
    """

    role: RoleMessageChatbot
    contenu: str


class GenerationReponsePort(ABC):
    """Contrat que doit respecter tout adaptateur de génération de réponses."""

    @abstractmethod
    def generer_reponse(
        self,
        question: str,
        format_attendu: FormatReponse,
        aide_extraction: str | None,
        extraits: list[ExtraitContexte],
        historique: list[TourConversation] | None = None,
    ) -> ReponseGeneree:
        """Génère une réponse à `question` à partir des `extraits` fournis en contexte.

        `historique`, si fourni, est réinjecté comme contexte conversationnel avant
        la question courante (permet les questions de suivi du chatbot).

        Lève `ErreurGenerationIndisponible` (transitoire) en cas de quota atteint
        ou de timeout réseau.
        """
        raise NotImplementedError
