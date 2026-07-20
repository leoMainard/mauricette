/**
 * Fonctions d'accès à l'API pour le feedback utilisateur (général par AO et par réponse).
 */

import { requeteJson } from "./client";
import type { Avis, FeedbackGeneral, FeedbackReponse, TypeErreurFeedback } from "./types";

export async function obtenirFeedbackGeneral(appelOffreId: string): Promise<FeedbackGeneral | null> {
  return requeteJson<FeedbackGeneral | null>(`/appels-offre/${appelOffreId}/feedback`);
}

export async function enregistrerFeedbackGeneral(
  appelOffreId: string,
  avis: Avis | null,
  commentaire: string | null,
): Promise<FeedbackGeneral> {
  return requeteJson<FeedbackGeneral>(`/appels-offre/${appelOffreId}/feedback`, {
    method: "PUT",
    body: JSON.stringify({ avis, commentaire }),
  });
}

export async function listerFeedbackReponses(appelOffreId: string): Promise<FeedbackReponse[]> {
  return requeteJson<FeedbackReponse[]>(`/appels-offre/${appelOffreId}/feedback-reponses`);
}

export interface DetailFeedbackReponse {
  avis: Avis | null;
  commentaire?: string | null;
  source_attendue?: string | null;
  citation_attendue?: string | null;
  type_erreur?: TypeErreurFeedback | null;
  details_erreur?: string | null;
}

export async function enregistrerFeedbackReponse(
  appelOffreId: string,
  questionReferentielId: string,
  detail: DetailFeedbackReponse,
): Promise<FeedbackReponse> {
  return requeteJson<FeedbackReponse>(
    `/appels-offre/${appelOffreId}/feedback-reponses/${questionReferentielId}`,
    {
      method: "PUT",
      body: JSON.stringify(detail),
    },
  );
}
