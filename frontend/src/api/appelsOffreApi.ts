/**
 * Fonctions d'accès à l'API pour les Appels d'Offres et leurs documents.
 * C'est le seul module qui connaît les routes HTTP exposées par le backend.
 */

import { requeteFormulaire, requeteJson } from "./client";
import type {
  AppelOffre,
  AppelOffreAvecStatistiques,
  AppelOffreDetail,
  ResultatDepotFichier,
} from "./types";

export async function creerAppelOffre(nom: string): Promise<AppelOffre> {
  return requeteJson<AppelOffre>("/appels-offre", {
    method: "POST",
    body: JSON.stringify({ nom }),
  });
}

export async function listerAppelsOffre(terme?: string): Promise<AppelOffreAvecStatistiques[]> {
  const suffixe = terme?.trim() ? `?recherche=${encodeURIComponent(terme.trim())}` : "";
  return requeteJson<AppelOffreAvecStatistiques[]>(`/appels-offre${suffixe}`);
}

export async function obtenirAppelOffre(appelOffreId: string): Promise<AppelOffreDetail> {
  return requeteJson<AppelOffreDetail>(`/appels-offre/${appelOffreId}`);
}

export async function renommerAppelOffre(appelOffreId: string, nom: string): Promise<AppelOffre> {
  return requeteJson<AppelOffre>(`/appels-offre/${appelOffreId}`, {
    method: "PATCH",
    body: JSON.stringify({ nom }),
  });
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

export async function supprimerDocument(appelOffreId: string, documentId: string): Promise<void> {
  return requeteJson<void>(`/appels-offre/${appelOffreId}/documents/${documentId}`, {
    method: "DELETE",
  });
}
