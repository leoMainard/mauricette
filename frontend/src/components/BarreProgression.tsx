interface Props {
  /** Pourcentage d'avancement (0-100), ou `null` si non applicable (ex: pas de référentiel attaché). */
  pourcentage: number | null;
}

export type SeuilAvancement = "critique" | "faible" | "moyenne" | "elevee";

/** Seuils partagés avec les KPIs/graphiques qui reprennent le même code couleur. */
export function seuilAvancement(pourcentage: number): SeuilAvancement {
  if (pourcentage <= 15) return "critique";
  if (pourcentage <= 50) return "faible";
  if (pourcentage <= 75) return "moyenne";
  return "elevee";
}

/** Couleurs figées (hors CSS) pour les graphiques recharts, alignées sur `App.css`. */
export const COULEURS_SEUIL: Record<SeuilAvancement, string> = {
  critique: "#d1372a",
  faible: "#f8a909",
  moyenne: "#31c6f5",
  elevee: "#009685",
};

/** Barre de progression générique (ex: avancement de l'analyse d'un AO). */
export function BarreProgression({ pourcentage }: Props) {
  if (pourcentage === null) {
    return <span className="texte-discret barre-progression__vide">Aucun référentiel</span>;
  }

  const valeur = Math.max(0, Math.min(100, pourcentage));

  return (
    <div className="barre-progression">
      <div className="barre-progression__piste">
        <div
          className={`barre-progression__remplissage barre-progression__remplissage--${seuilAvancement(valeur)}`}
          style={{ width: `${valeur}%` }}
        />
      </div>
      <span className="barre-progression__valeur">{valeur}%</span>
    </div>
  );
}
