/**
 * Bucketing temporel (jour/semaine/mois) partagé par tous les graphiques d'évolution
 * de l'application (tableau de bord AO, tableau de bord admin).
 */

export type Granularite = "jour" | "semaine" | "mois";

export const LIBELLES_GRANULARITE: Record<Granularite, string> = {
  jour: "Jour",
  semaine: "Semaine",
  mois: "Mois",
};

const NB_PERIODES_PAR_DEFAUT: Record<Granularite, number> = { jour: 14, semaine: 8, mois: 6 };

/** Clé "YYYY-MM-DD" à partir des champs de calendrier LOCAUX d'une date (jamais via
 * `toISOString`, qui convertit en UTC et peut décaler la date d'un jour selon le
 * fuseau horaire — source d'un vrai bug de comptage déjà observé sur ces graphiques). */
export function cleJour(date: Date): string {
  const annee = date.getFullYear();
  const mois = String(date.getMonth() + 1).padStart(2, "0");
  const jour = String(date.getDate()).padStart(2, "0");
  return `${annee}-${mois}-${jour}`;
}

export function lundiDeLaSemaine(date: Date): Date {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const jourSemaine = d.getDay();
  const decalage = jourSemaine === 0 ? -6 : 1 - jourSemaine;
  d.setDate(d.getDate() + decalage);
  return d;
}

export function premierDuMois(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function cleSelonGranularite(date: Date, granularite: Granularite): string {
  if (granularite === "jour") return cleJour(date);
  if (granularite === "semaine") return cleJour(lundiDeLaSemaine(date));
  return cleJour(premierDuMois(date));
}

export function libelleSelonGranularite(date: Date, granularite: Granularite): string {
  if (granularite === "mois") {
    return date.toLocaleDateString("fr-FR", { month: "short", year: "2-digit" });
  }
  return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

/** Génère la liste des périodes (clé + libellé) des `n` dernières unités de granularité
 * jusqu'à aujourd'hui inclus. `n` par défaut : 14 jours / 8 semaines / 6 mois. */
export function genererPeriodes(
  granularite: Granularite,
  n: number = NB_PERIODES_PAR_DEFAUT[granularite],
): { cle: string; libelle: string }[] {
  const maintenant = new Date();
  const reference =
    granularite === "jour"
      ? new Date(maintenant.getFullYear(), maintenant.getMonth(), maintenant.getDate())
      : granularite === "semaine"
        ? lundiDeLaSemaine(maintenant)
        : premierDuMois(maintenant);

  return Array.from({ length: n }, (_, i) => {
    const d = new Date(reference);
    if (granularite === "jour") d.setDate(d.getDate() - (n - 1 - i));
    else if (granularite === "semaine") d.setDate(d.getDate() - (n - 1 - i) * 7);
    else d.setMonth(d.getMonth() - (n - 1 - i));
    return { cle: cleJour(d), libelle: libelleSelonGranularite(d, granularite) };
  });
}
