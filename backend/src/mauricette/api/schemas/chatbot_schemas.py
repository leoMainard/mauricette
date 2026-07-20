"""Schémas Pydantic (contrats HTTP) pour le chatbot d'un Appel d'Offres."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mauricette.api.schemas.reponse_question_schemas import CitationReponse
from mauricette.domaine.entites.enums import RoleMessageChatbot
from mauricette.domaine.entites.message_chatbot import MessageChatbot


class PoserQuestionChatbotRequete(BaseModel):
    """Corps de requête pour poser une question au chatbot."""

    question: str = Field(min_length=1, max_length=2000)


class MessageChatbotReponse(BaseModel):
    """Représentation HTTP d'un message du chatbot (question ou réponse)."""

    id: UUID
    appel_offre_id: UUID
    role: RoleMessageChatbot
    contenu: str | None
    score_confiance: float | None
    citations: list[CitationReponse]
    date_creation: datetime

    @classmethod
    def depuis_entite(cls, entite: MessageChatbot) -> "MessageChatbotReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            appel_offre_id=entite.appel_offre_id,
            role=entite.role,
            contenu=entite.contenu,
            score_confiance=entite.score_confiance,
            citations=[CitationReponse.depuis_entite(c) for c in entite.citations],
            date_creation=entite.date_creation,
        )
