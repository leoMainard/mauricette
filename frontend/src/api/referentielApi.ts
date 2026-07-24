/**
 * Fonctions d'accès à l'API pour les référentiels, leurs sections et leurs questions.
 */

import { requeteJson } from "./client";
import type {
  ContenuQuestionReferentiel,
  ContenuReferentiel,
  DetailReferentiel,
  QuestionReferentiel,
  Referentiel,
  ReferentielAvecStatistiques,
  SectionReferentiel,
} from "./types";

// --- Référentiels ---

export async function creerReferentiel(contenu: ContenuReferentiel): Promise<Referentiel> {
  return requeteJson<Referentiel>("/referentiels", {
    method: "POST",
    body: JSON.stringify(contenu),
  });
}

export async function listerReferentiels(terme?: string): Promise<ReferentielAvecStatistiques[]> {
  const suffixe = terme?.trim() ? `?recherche=${encodeURIComponent(terme.trim())}` : "";
  return requeteJson<ReferentielAvecStatistiques[]>(`/referentiels${suffixe}`);
}

export async function obtenirReferentiel(referentielId: string): Promise<DetailReferentiel> {
  return requeteJson<DetailReferentiel>(`/referentiels/${referentielId}`);
}

export async function modifierReferentiel(
  referentielId: string,
  contenu: ContenuReferentiel,
): Promise<Referentiel> {
  return requeteJson<Referentiel>(`/referentiels/${referentielId}`, {
    method: "PATCH",
    body: JSON.stringify(contenu),
  });
}

export async function supprimerReferentiel(referentielId: string): Promise<void> {
  return requeteJson<void>(`/referentiels/${referentielId}`, { method: "DELETE" });
}

// --- Sections ---

export async function creerSection(referentielId: string, nom: string): Promise<SectionReferentiel> {
  return requeteJson<SectionReferentiel>(`/referentiels/${referentielId}/sections`, {
    method: "POST",
    body: JSON.stringify({ nom }),
  });
}

export async function modifierSection(sectionId: string, nom: string): Promise<SectionReferentiel> {
  return requeteJson<SectionReferentiel>(`/sections/${sectionId}`, {
    method: "PATCH",
    body: JSON.stringify({ nom }),
  });
}

export async function supprimerSection(sectionId: string): Promise<void> {
  return requeteJson<void>(`/sections/${sectionId}`, { method: "DELETE" });
}

export async function reordonnerSections(
  referentielId: string,
  idsOrdonnes: string[],
): Promise<SectionReferentiel[]> {
  return requeteJson<SectionReferentiel[]>(`/referentiels/${referentielId}/sections/ordre`, {
    method: "PATCH",
    body: JSON.stringify({ ids_ordonnes: idsOrdonnes }),
  });
}

// --- Questions ---

export async function creerQuestionReferentiel(
  sectionId: string,
  contenu: ContenuQuestionReferentiel,
): Promise<QuestionReferentiel> {
  return requeteJson<QuestionReferentiel>(`/sections/${sectionId}/questions`, {
    method: "POST",
    body: JSON.stringify(contenu),
  });
}

export async function modifierQuestionReferentiel(
  questionId: string,
  contenu: ContenuQuestionReferentiel,
): Promise<QuestionReferentiel> {
  return requeteJson<QuestionReferentiel>(`/questions/${questionId}`, {
    method: "PATCH",
    body: JSON.stringify(contenu),
  });
}

export async function changerActivationQuestion(
  questionId: string,
  actif: boolean,
): Promise<QuestionReferentiel> {
  return requeteJson<QuestionReferentiel>(`/questions/${questionId}/activation`, {
    method: "PATCH",
    body: JSON.stringify({ actif }),
  });
}

export async function supprimerQuestionReferentiel(questionId: string): Promise<void> {
  return requeteJson<void>(`/questions/${questionId}`, { method: "DELETE" });
}

export async function reordonnerQuestions(
  sectionId: string,
  idsOrdonnes: string[],
): Promise<QuestionReferentiel[]> {
  return requeteJson<QuestionReferentiel[]>(`/sections/${sectionId}/questions/ordre`, {
    method: "PATCH",
    body: JSON.stringify({ ids_ordonnes: idsOrdonnes }),
  });
}

// --- Rattachement référentiel ↔ Appel d'Offres ---

export async function listerReferentielsDeAppelOffre(appelOffreId: string): Promise<Referentiel[]> {
  return requeteJson<Referentiel[]>(`/appels-offre/${appelOffreId}/referentiels`);
}

export async function attacherReferentiel(
  appelOffreId: string,
  referentielId: string,
): Promise<Referentiel[]> {
  return requeteJson<Referentiel[]>(`/appels-offre/${appelOffreId}/referentiels`, {
    method: "POST",
    body: JSON.stringify({ referentiel_id: referentielId }),
  });
}

export async function detacherReferentiel(appelOffreId: string, referentielId: string): Promise<void> {
  return requeteJson<void>(`/appels-offre/${appelOffreId}/referentiels/${referentielId}`, {
    method: "DELETE",
  });
}
