/**
 * Fonctions d'accès à l'API pour les Appels d'Offres et leurs documents.
 * C'est le seul module qui connaît les routes HTTP exposées par le backend.
 */

import { requeteFormulaire, requeteJson, URL_BASE_API } from "./client";
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

export async function supprimerAppelOffre(appelOffreId: string): Promise<void> {
  return requeteJson<void>(`/appels-offre/${appelOffreId}`, { method: "DELETE" });
}

/** URL du contenu binaire d'un document, pour aperçu (iframe, img, ou fetch côté JS). */
export function urlContenuDocument(appelOffreId: string, documentId: string): string {
  return `${URL_BASE_API}/appels-offre/${appelOffreId}/documents/${documentId}/contenu`;
}

/** URL de téléchargement d'un document (force l'enregistrement plutôt que l'aperçu). */
export function urlTelechargementDocument(appelOffreId: string, documentId: string): string {
  return `${URL_BASE_API}/appels-offre/${appelOffreId}/documents/${documentId}/contenu?telecharger=true`;
}

/** URL de téléchargement de tous les documents d'un AO regroupés en ZIP. */
export function urlTelechargementDocumentsZip(appelOffreId: string): string {
  return `${URL_BASE_API}/appels-offre/${appelOffreId}/documents/zip`;
}

/** URL d'export du questionnaire (réponses) d'un AO dans le format demandé. */
export function urlExportReponses(
  appelOffreId: string,
  format: "pdf" | "docx" | "xlsx",
): string {
  return `${URL_BASE_API}/appels-offre/${appelOffreId}/reponses/export?format=${format}`;
}
