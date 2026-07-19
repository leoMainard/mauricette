/**
 * Types partagés avec l'API backend (miroir des schémas Pydantic).
 * Toute évolution des schémas côté backend doit être reportée ici.
 */

export type StatutAppelOffre = "brouillon" | "en_cours" | "traite" | "archive";

export type StatutDocument = "en_attente" | "televerse" | "en_erreur" | "traite";

export interface AppelOffre {
  id: string;
  nom: string;
  cree_par: string;
  statut: StatutAppelOffre;
  date_creation: string;
  date_maj: string;
}

export interface DocumentDepose {
  id: string;
  appel_offre_id: string;
  nom_original: string;
  type_mime: string;
  taille_octets: number;
  statut: StatutDocument;
  date_creation: string;
  date_maj: string;
}

export interface AppelOffreDetail {
  appel_offre: AppelOffre;
  documents: DocumentDepose[];
}

/** Bilan du dépôt d'un fichier : documents créés (peut être plusieurs si zip) et doublons ignorés. */
export interface ResultatDepotFichier {
  documents_crees: DocumentDepose[];
  doublons_ignores: string[];
}
