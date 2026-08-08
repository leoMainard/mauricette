import { Gauge, Search, ThumbsUp } from "lucide-react";
import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ReferentielAvecStatistiques, StatistiquesQualite } from "../../api/types";

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";
const VERT = "#009685";
const CYAN_MID = "#31c6f5";
const ORANGE = "#f8a909";
const MARINE = "#133478";

const TRANCHES = [
  { min: 0, max: 0.25, libelle: "0-25%" },
  { min: 0.25, max: 0.5, libelle: "25-50%" },
  { min: 0.5, max: 0.75, libelle: "50-75%" },
  { min: 0.75, max: 1.01, libelle: "75-100%" },
];

const NOMBRE_REFERENTIELS_AFFICHES = 10;

interface Props {
  qualite: StatistiquesQualite;
  referentiels: ReferentielAvecStatistiques[];
}

/** Onglet admin : qualité des réponses générées par le RAG (confiance, taux de
 * réponses trouvées, taux de validation, référentiels les plus problématiques). */
export function OngletQualiteIA({ qualite, referentiels }: Props) {
  const nomParReferentiel = useMemo(
    () => new Map(referentiels.map((r) => [r.referentiel.id, r.referentiel.nom])),
    [referentiels],
  );

  const scoreMoyen = useMemo(() => {
    if (qualite.scores_confiance.length === 0) return null;
    const somme = qualite.scores_confiance.reduce((acc, s) => acc + s, 0);
    return Math.round((somme / qualite.scores_confiance.length) * 100);
  }, [qualite.scores_confiance]);

  const distributionConfiance = useMemo(
    () =>
      TRANCHES.map((tranche) => ({
        libelle: tranche.libelle,
        nombre: qualite.scores_confiance.filter((s) => s >= tranche.min && s < tranche.max).length,
      })),
    [qualite.scores_confiance],
  );

  const totalAvecSans = useMemo(() => {
    let avec = 0;
    let sans = 0;
    for (const { avec: a, sans: s } of Object.values(qualite.sans_contenu_par_referentiel)) {
      avec += a;
      sans += s;
    }
    return { avec, sans };
  }, [qualite.sans_contenu_par_referentiel]);

  const tauxTrouve =
    totalAvecSans.avec + totalAvecSans.sans > 0
      ? Math.round((totalAvecSans.avec / (totalAvecSans.avec + totalAvecSans.sans)) * 100)
      : null;

  const donneesStatut = Object.entries(qualite.reponses_par_statut).map(([statut, valeur]) => ({
    statut,
    libelle: statut === "valide_utilisateur" ? "Validée" : "Générée (non validée)",
    valeur,
  }));

  const referentielsProblematiques = useMemo(() => {
    return Object.entries(qualite.sans_contenu_par_referentiel)
      .map(([id, { avec, sans }]) => ({
        nom: nomParReferentiel.get(id) ?? id,
        sans,
        taux: avec + sans > 0 ? Math.round((sans / (avec + sans)) * 100) : 0,
      }))
      .filter((r) => r.sans > 0)
      .sort((a, b) => b.taux - a.taux)
      .slice(0, NOMBRE_REFERENTIELS_AFFICHES);
  }, [qualite.sans_contenu_par_referentiel, nomParReferentiel]);

  return (
    <>
      <div className="grille-kpi">
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <Gauge size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Score de confiance moyen</div>
            <div className="carte-kpi__valeur">{scoreMoyen !== null ? `${scoreMoyen}%` : "—"}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--cyan">
            <Search size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Réponses trouvées</div>
            <div className="carte-kpi__valeur">{tauxTrouve !== null ? `${tauxTrouve}%` : "—"}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--vert">
            <ThumbsUp size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Total réponses générées</div>
            <div className="carte-kpi__valeur">{qualite.total_reponses}</div>
          </div>
        </div>
      </div>

      <div className="grille-graphiques">
        <div className="carte carte--graphique carte--graphique-donut">
          <h2>Réponses générées vs validées</h2>
          {donneesStatut.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={donneesStatut} dataKey="valeur" nameKey="libelle" innerRadius={40} outerRadius={65} paddingAngle={2}>
                  {donneesStatut.map((entree) => (
                    <Cell key={entree.statut} fill={entree.statut === "valide_utilisateur" ? VERT : CYAN_MID} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="texte-discret">Aucune réponse générée pour le moment.</p>
          )}
        </div>

        <div className="carte carte--graphique carte--graphique-activite">
          <h2>Distribution des scores de confiance</h2>
          {qualite.scores_confiance.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distributionConfiance}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={GRIS_GRILLE} />
                <XAxis dataKey="libelle" tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} width={28} />
                <Tooltip />
                <Bar dataKey="nombre" name="Réponses" fill={MARINE} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="texte-discret">Aucun score de confiance pour le moment.</p>
          )}
        </div>
      </div>

      {referentielsProblematiques.length > 0 && (
        <div className="carte carte--graphique">
          <h2>Référentiels avec le plus de réponses non trouvées</h2>
          <ResponsiveContainer width="100%" height={Math.max(180, referentielsProblematiques.length * 36)}>
            <BarChart data={referentielsProblematiques} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
              <XAxis type="number" unit="%" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <YAxis type="category" dataKey="nom" width={170} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <Tooltip />
              <Bar dataKey="taux" name="Taux de non-réponse" fill={ORANGE} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </>
  );
}
