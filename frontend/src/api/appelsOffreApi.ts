/**
 * Fonctions d'accès à l'API pour les Appels d'Offres et leurs documents.
 * C'est le seul module qui connaît les routes HTTP exposées par le backend.
 */

import { requeteFormulaire, requeteJson } from "./client";
import type { AppelOffre, AppelOffreDetail, ResultatDepotFichier } from "./types";

export async function creerAppelOffre(nom: string): Promise<AppelOffre> {
  return requeteJson<AppelOffre>("/appels-offre", {
    method: "POST",
    body: JSON.stringify({ nom }),
  });
}

export async function listerAppelsOffre(): Promise<AppelOffre[]> {
  return requeteJson<AppelOffre[]>("/appels-offre");
}

export async function obtenirAppelOffre(appelOffreId: string): Promise<AppelOffreDetail> {
  return requeteJson<AppelOffreDetail>(`/appels-offre/${appelOffreId}`);
}

export async function deposerDocument(
  appelOffreId: string,
  fichier: File,
): Promise<ResultatDepotFichier> {
  const formulaire = new FormData();
  formulaire.append("fichier", fichier);
  return requeteFormulaire<ResultatDepotFichier>(
    `/appels-offre/${appelOffreId}/documents`,
    formulaire,
  );
}
