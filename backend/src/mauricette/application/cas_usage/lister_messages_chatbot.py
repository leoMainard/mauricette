"""Cas d'usage : lister l'historique de conversation du chatbot d'un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from mauricette.domaine.entites.message_chatbot import MessageChatbot
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.message_chatbot_repository import MessageChatbotRepositoryPort


class ListerMessagesChatbot:
    """Retourne tout l'historique de conversation du chatbot d'un AO, du plus ancien au plus récent."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_messages: MessageChatbotRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_messages = depot_messages

    def executer(self, appel_offre_id: UUID) -> list[MessageChatbot]:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {appel_offre_id}")
        return self._depot_messages.lister_par_appel_offre(appel_offre_id)
