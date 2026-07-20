"""Entité métier : message du chatbot d'un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import RoleMessageChatbot
from mauricette.domaine.entites.reponse_question import Citation


@dataclass
class MessageChatbot:
    """Un message (question ou réponse) dans le fil de discussion du chatbot d'un AO.

    Contrairement à `ReponseQuestion`, un message est immuable une fois créé (pas
    de validation utilisateur, pas de régénération) : c'est un journal de
    conversation en ajout seul, pas une réponse qu'on met à jour.
    """

    appel_offre_id: UUID
    role: RoleMessageChatbot
    contenu: str | None
    id: UUID = field(default_factory=uuid4)
    score_confiance: float | None = None
    citations: list[Citation] = field(default_factory=list)
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
