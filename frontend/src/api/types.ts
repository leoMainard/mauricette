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
  questions_actives: number;
  reponses_generees: number;
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

export type RoleMessageChatbot = "utilisateur" | "assistant";

/** Message (question ou réponse) du fil de discussion du chatbot d'un AO. */
export interface MessageChatbot {
  id: string;
  appel_offre_id: string;
  role: RoleMessageChatbot;
  contenu: string | null;
  score_confiance: number | null;
  citations: Citation[];
  date_creation: string;
}

export type Avis = "positif" | "negatif";

export type TypeErreurFeedback =
  | "information_incorrecte"
  | "information_incomplete"
  | "mauvaise_source"
  | "source_manquante"
  | "format_inadapte"
  | "autre";

/** Avis global sur l'aide apportée par Mauricette pour un AO (un seul par AO). */
export interface FeedbackGeneral {
  id: string;
  appel_offre_id: string;
  avis: Avis | null;
  commentaire: string | null;
  date_creation: string;
  date_maj: string;
}

/** Avis sur la réponse à une question de référentiel, pour un AO (un seul par question). */
export interface FeedbackReponse {
  id: string;
  appel_offre_id: string;
  question_referentiel_id: string;
  avis: Avis | null;
  contenu_reponse_snapshot: string | null;
  commentaire: string | null;
  source_attendue: string | null;
  citation_attendue: string | null;
  type_erreur: TypeErreurFeedback | null;
  details_erreur: string | null;
  date_creation: string;
  date_maj: string;
}

/** Nombre de documents dont l'analyse s'est terminée durant un jour donné. */
export interface VolumeJour {
  jour: string;
  nombre: number;
}

export type StatutUtilisateur = "user" | "admin";

export interface Utilisateur {
  id: string;
  email: string;
  nom: string;
  statut: StatutUtilisateur;
  groupe_id: string | null;
  date_creation: string;
  date_maj: string;
}

export interface GroupeUtilisateur {
  id: string;
  nom: string;
  date_creation: string;
}
