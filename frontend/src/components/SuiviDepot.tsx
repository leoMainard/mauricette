export interface SuiviFichier {
  nomFichier: string;
  statut: "en_cours" | "succes" | "doublon" | "erreur";
  message?: string;
}

interface Props {
  suivis: SuiviFichier[];
}

const LIBELLES: Record<SuiviFichier["statut"], string> = {
  en_cours: "Envoi en cours...",
  succes: "Déposé ✓",
  doublon: "Déjà présent, ignoré",
  erreur: "Erreur",
};

/** Affiche l'avancement de l'envoi de chaque fichier vers le backend. */
export function SuiviDepot({ suivis }: Props) {
  if (suivis.length === 0) {
    return null;
  }

  return (
    <ul className="liste-suivi">
      {suivis.map((suivi, index) => (
        <li key={`${suivi.nomFichier}-${index}`} className={`suivi suivi--${suivi.statut}`}>
          <span>{suivi.nomFichier}</span>
          <span>{LIBELLES[suivi.statut]}{suivi.statut === "erreur" && suivi.message ? ` : ${suivi.message}` : ""}</span>
        </li>
      ))}
    </ul>
  );
}
