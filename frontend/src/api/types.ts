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

/** Un Appel d'Offres accompagné du nombre et du poids total de ses documents (vue liste). */
export interface AppelOffreAvecStatistiques {
  appel_offre: AppelOffre;
  nombre_documents: number;
  taille_totale_octets: number;
  en_erreur_analyse: boolean;
}

/** Bilan du dépôt d'un fichier : documents créés (peut être plusieurs si zip) et doublons ignorés. */
export interface ResultatDepotFichier {
  documents_crees: DocumentDepose[];
  doublons_ignores: string[];
}

export type FormatReponse =
  | "oui_non"
  | "montant"
  | "date"
  | "pourcentage"
  | "liste"
  | "texte_libre"
  | "autre";

export interface Referentiel {
  id: string;
  nom: string;
  description: string | null;
  actif_par_defaut: boolean;
  date_creation: string;
  date_maj: string;
}

/** Un référentiel accompagné de ses statistiques d'utilisation (vue liste). */
export interface ReferentielAvecStatistiques {
  referentiel: Referentiel;
  nombre_sections: number;
  nombre_questions_actives: number;
  nombre_ao_concernes: number;
}

/** Contenu envoyé à la création ou à la modification d'un référentiel. */
export interface ContenuReferentiel {
  nom: string;
  description?: string | null;
  actif_par_defaut: boolean;
}

export interface SectionReferentiel {
  id: string;
  referentiel_id: string;
  nom: string;
  ordre: number;
  date_creation: string;
}

export interface QuestionReferentiel {
  id: string;
  section_id: string;
  question: string;
  format_reponse: FormatReponse;
  aide_extraction: string | null;
  obligatoire: boolean;
  actif: boolean;
  ordre: number;
  date_creation: string;
  date_maj: string;
}

/** Contenu envoyé à la création ou à la modification d'une question de référentiel. */
export interface ContenuQuestionReferentiel {
  question: string;
  format_reponse: FormatReponse;
  aide_extraction?: string | null;
  obligatoire: boolean;
}

export interface SectionAvecQuestions {
  section: SectionReferentiel;
  questions: QuestionReferentiel[];
}

/** Détail complet d'un référentiel : ses sections (avec leurs questions) et ses statistiques. */
export interface DetailReferentiel {
  referentiel: Referentiel;
  sections: SectionAvecQuestions[];
  nombre_ao_concernes: number;
}

export type StatutEtape = "en_attente" | "en_cours" | "reussi" | "echec";

export interface EtapeTraitement {
  statut: StatutEtape;
  message_erreur: string | null;
  date_maj: string | null;
}

/** Suivi du pipeline RAG (extraction, découpage, embedding) d'un document. */
export interface DocumentTraitementRag {
  document_id: string;
  extraction: EtapeTraitement;
  decoupage: EtapeTraitement;
  embedding: EtapeTraitement;
  statut_global: StatutEtape;
}

export type StatutTache = "en_attente" | "en_cours" | "reussi" | "echec";

/** État de la dernière analyse (régénération des réponses) déclenchée pour un AO. */
export interface EtatAnalyse {
  statut: StatutTache;
  message_erreur: string | null;
  tentatives: number;
}

export type StatutReponse = "generee" | "valide_utilisateur";

export interface Citation {
  chunk_id: string;
  document_id: string;
  document_nom: string;
  page_debut: number | null;
  page_fin: number | null;
  titre_section: string | null;
}

/** Réponse générée par le RAG pour une question de référentiel, sur un AO donné. */
export interface ReponseQuestion {
  id: string;
  appel_offre_id: string;
  question_referentiel_id: string;
  contenu: string | null;
  score_confiance: number | null;
  statut: StatutReponse;
  citations: Citation[];
  date_creation: string;
  date_maj: string;
}
