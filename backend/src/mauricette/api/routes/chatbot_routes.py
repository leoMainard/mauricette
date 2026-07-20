"""Routes HTTP relatives au chatbot d'un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_lister_messages_chatbot,
    obtenir_cas_usage_poser_question_chatbot,
)
from mauricette.api.schemas.chatbot_schemas import (
    MessageChatbotReponse,
    PoserQuestionChatbotRequete,
)
from mauricette.application.cas_usage.lister_messages_chatbot import ListerMessagesChatbot
from mauricette.application.cas_usage.poser_question_chatbot import (
    CommandePoserQuestionChatbot,
    PoserQuestionChatbot,
)
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurGenerationIndisponible

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}/chatbot", tags=["Chatbot"])


@routeur.get("/messages", response_model=list[MessageChatbotReponse])
def lister_messages(
    appel_offre_id: UUID,
    cas_usage: ListerMessagesChatbot = Depends(obtenir_cas_usage_lister_messages_chatbot),
) -> list[MessageChatbotReponse]:
    """Retourne tout l'historique de conversation du chatbot pour cet AO."""
    try:
        messages = cas_usage.executer(appel_offre_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return [MessageChatbotReponse.depuis_entite(message) for message in messages]


@routeur.post("/messages", response_model=MessageChatbotReponse, status_code=status.HTTP_201_CREATED)
def poser_question(
    appel_offre_id: UUID,
    requete: PoserQuestionChatbotRequete,
    cas_usage: PoserQuestionChatbot = Depends(obtenir_cas_usage_poser_question_chatbot),
) -> MessageChatbotReponse:
    """Pose une question libre au chatbot et retourne la réponse générée (l'assistant seul —
    le message utilisateur, déjà connu de l'appelant, n'a pas besoin d'être renvoyé)."""
    try:
        message = cas_usage.executer(
            CommandePoserQuestionChatbot(appel_offre_id=appel_offre_id, question=requete.question)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except ErreurGenerationIndisponible as erreur:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(erreur)) from erreur
    return MessageChatbotReponse.depuis_entite(message)
