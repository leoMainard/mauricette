import type { StatutEtape } from "../api/types";
import { Badge } from "./Badge";

// Réutilise les classes CSS des badges de statut de document (aucun style
// supplémentaire nécessaire) : "reussi" -> vert "traite", "echec" -> rouge "en_erreur".
const CLASSE_PAR_STATUT: Record<StatutEtape, string> = {
  en_attente: "en_attente",
  en_cours: "en_cours",
  reussi: "traite",
  echec: "en_erreur",
};

const LIBELLE_PAR_STATUT: Record<StatutEtape, string> = {
  en_attente: "En attente",
  en_cours: "Traitement en cours",
  reussi: "Traité",
  echec: "Erreur",
};

interface Props {
  statut: StatutEtape;
}

/** Pastille de statut pour une étape (ou l'état global) du pipeline RAG d'un document. */
export function BadgeEtapeTraitement({ statut }: Props) {
  return <Badge statut={CLASSE_PAR_STATUT[statut]} libelle={LIBELLE_PAR_STATUT[statut]} />;
}
