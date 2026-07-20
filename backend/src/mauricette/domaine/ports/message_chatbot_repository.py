"""Port (interface) pour la persistance des messages du chatbot d'un Appel d'Offres."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.message_chatbot import MessageChatbot


class MessageChatbotRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des messages du chatbot."""

    @abstractmethod
    def ajouter(self, message: MessageChatbot) -> None:
        """Persiste un nouveau message (question ou réponse)."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[MessageChatbot]:
        """Retourne tout l'historique de conversation d'un AO, du plus ancien au plus récent.

        Utilisé pour l'affichage complet à l'ouverture de l'onglet.
        """
        raise NotImplementedError

    @abstractmethod
    def lister_derniers(self, appel_offre_id: UUID, limite: int) -> list[MessageChatbot]:
        """Retourne les `limite` derniers messages d'un AO, du plus ancien au plus récent.

        Utilisé pour construire le contexte conversationnel envoyé au modèle de
        génération, sans charger tout l'historique d'une conversation qui peut
        devenir longue.
        """
        raise NotImplementedError
