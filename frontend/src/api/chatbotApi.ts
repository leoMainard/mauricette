/**
 * Fonctions d'accès à l'API pour le chatbot d'un Appel d'Offres.
 */

import { requeteJson } from "./client";
import type { MessageChatbot } from "./types";

export async function listerMessagesChatbot(appelOffreId: string): Promise<MessageChatbot[]> {
  return requeteJson<MessageChatbot[]>(`/appels-offre/${appelOffreId}/chatbot/messages`);
}

export async function poserQuestionChatbot(
  appelOffreId: string,
  question: string,
): Promise<MessageChatbot> {
  return requeteJson<MessageChatbot>(`/appels-offre/${appelOffreId}/chatbot/messages`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
