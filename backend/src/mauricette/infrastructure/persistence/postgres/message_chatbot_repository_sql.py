"""Adaptateur PostgreSQL du port `MessageChatbotRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.message_chatbot import MessageChatbot
from mauricette.domaine.ports.message_chatbot_repository import MessageChatbotRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    message_chatbot_vers_entite,
    message_chatbot_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import MessageChatbotModele


class MessageChatbotRepositorySQL(MessageChatbotRepositoryPort):
    """Implémentation PostgreSQL du repository des messages du chatbot."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, message: MessageChatbot) -> None:
        self._session.add(message_chatbot_vers_modele(message))
        self._session.commit()

    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[MessageChatbot]:
        requete = (
            select(MessageChatbotModele)
            .where(MessageChatbotModele.appel_offre_id == appel_offre_id)
            .order_by(MessageChatbotModele.date_creation)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [message_chatbot_vers_entite(modele) for modele in modeles]

    def lister_derniers(self, appel_offre_id: UUID, limite: int) -> list[MessageChatbot]:
        requete = (
            select(MessageChatbotModele)
            .where(MessageChatbotModele.appel_offre_id == appel_offre_id)
            .order_by(MessageChatbotModele.date_creation.desc())
            .limit(limite)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [message_chatbot_vers_entite(modele) for modele in reversed(modeles)]
