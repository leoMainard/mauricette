/**
 * Fonctions d'accès à l'API pour les statistiques globales du tableau de bord.
 */

import { requeteJson } from "./client";
import type { VolumeJour } from "./types";

export async function obtenirVolumeDocumentsParJour(): Promise<VolumeJour[]> {
  return requeteJson<VolumeJour[]>("/statistiques/documents-par-jour");
}
