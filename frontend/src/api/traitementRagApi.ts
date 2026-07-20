/**
 * Fonctions d'accès à l'API pour le suivi du pipeline RAG et les réponses générées.
 */

import { requeteJson } from "./client";
import type { DocumentTraitementRag, EtatAnalyse, ReponseQuestion } from "./types";

export async function obtenirTraitementAppelOffre(
  appelOffreId: string,
): Promise<DocumentTraitementRag[]> {
  return requeteJson<DocumentTraitementRag[]>(`/appels-offre/${appelOffreId}/traitement`);
}

export async function relancerDocument(appelOffreId: string, documentId: string): Promise<void> {
  return requeteJson<void>(
    `/appels-offre/${appelOffreId}/documents/${documentId}/traitement/relancer`,
    { method: "POST" },
  );
}

export async function listerReponsesAppelOffre(appelOffreId: string): Promise<ReponseQuestion[]> {
  return requeteJson<ReponseQuestion[]>(`/appels-offre/${appelOffreId}/reponses`);
}

export async function reanalyserAppelOffre(appelOffreId: string): Promise<void> {
  return requeteJson<void>(`/appels-offre/${appelOffreId}/reponses/reanalyser`, { method: "POST" });
}

export async function obtenirEtatAnalyseAppelOffre(
  appelOffreId: string,
): Promise<EtatAnalyse | null> {
  return requeteJson<EtatAnalyse | null>(`/appels-offre/${appelOffreId}/reponses/etat-analyse`);
}

export async function validerReponse(reponseId: string): Promise<ReponseQuestion> {
  return requeteJson<ReponseQuestion>(`/reponses/${reponseId}/valider`, { method: "PATCH" });
}
