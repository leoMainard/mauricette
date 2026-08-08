/**
 * Fonctions d'accès à l'API pour le tableau de bord admin (vue globale de l'application).
 */

import { requeteJson } from "./client";
import type {
  AppelOffreAvecStatistiques,
  ReferentielAvecStatistiques,
  StatistiquesFeedback,
  StatistiquesPipeline,
  StatistiquesQualite,
} from "./types";

/** Tous les AO de l'application, sans filtre de visibilité (admin uniquement). */
export async function listerTousLesAppelsOffre(): Promise<AppelOffreAvecStatistiques[]> {
  return requeteJson<AppelOffreAvecStatistiques[]>("/admin/appels-offre");
}

/** Tous les référentiels de l'application, sans filtre de visibilité (admin uniquement). */
export async function listerTousLesReferentiels(): Promise<ReferentielAvecStatistiques[]> {
  return requeteJson<ReferentielAvecStatistiques[]>("/admin/referentiels");
}

export async function obtenirStatistiquesFeedback(): Promise<StatistiquesFeedback> {
  return requeteJson<StatistiquesFeedback>("/admin/feedback");
}

export async function obtenirStatistiquesPipeline(): Promise<StatistiquesPipeline> {
  return requeteJson<StatistiquesPipeline>("/admin/pipeline");
}

export async function obtenirStatistiquesQualite(): Promise<StatistiquesQualite> {
  return requeteJson<StatistiquesQualite>("/admin/qualite");
}
