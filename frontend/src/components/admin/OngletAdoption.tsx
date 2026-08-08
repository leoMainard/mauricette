import { UserCheck, UserPlus } from "lucide-react";
import { useMemo, useState } from "react";
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { AppelOffreAvecStatistiques, Utilisateur } from "../../api/types";
import type { Granularite } from "../../utils/granularite";
import { cleSelonGranularite, genererPeriodes, LIBELLES_GRANULARITE } from "../../utils/granularite";

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";
const COULEUR_NOUVEAUX = "#31c6f5";
const COULEUR_CUMULE = "#133478";

const JOURS_ACTIVITE_RECENTE = 30;

interface Props {
  utilisateurs: Utilisateur[];
  appelsOffre: AppelOffreAvecStatistiques[];
}

/** Onglet admin : adoption et croissance dans le temps (inscriptions, utilisateurs actifs). */
export function OngletAdoption({ utilisateurs, appelsOffre }: Props) {
  const [granularite, setGranularite] = useState<Granularite>("semaine");

  const utilisateursActifs = useMemo(() => {
    const seuil = new Date();
    seuil.setDate(seuil.getDate() - JOURS_ACTIVITE_RECENTE);
    const proprietairesActifs = new Set(
      appelsOffre
        .filter((ao) => new Date(ao.appel_offre.date_creation) >= seuil)
        .map((ao) => ao.appel_offre.cree_par_id)
        .filter((id): id is string => id !== null),
    );
    return proprietairesActifs.size;
  }, [appelsOffre]);

  const donneesInscriptions = useMemo(() => {
    const periodes = genererPeriodes(granularite);
    const parCle = new Map(periodes.map((p) => [p.cle, 0]));
    const premiereCle = periodes[0].cle;
    let avantFenetre = 0;

    for (const utilisateur of utilisateurs) {
      const cle = cleSelonGranularite(new Date(utilisateur.date_creation), granularite);
      if (parCle.has(cle)) {
        parCle.set(cle, parCle.get(cle)! + 1);
      } else if (cle < premiereCle) {
        avantFenetre += 1;
      }
    }

    let cumul = avantFenetre;
    return periodes.map((p) => {
      const nouveaux = parCle.get(p.cle)!;
      cumul += nouveaux;
      return { libelle: p.libelle, nouveaux, cumule: cumul };
    });
  }, [utilisateurs, granularite]);

  return (
    <>
      <div className="grille-kpi">
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <UserPlus size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Utilisateurs inscrits</div>
            <div className="carte-kpi__valeur">{utilisateurs.length}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--vert">
            <UserCheck size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Actifs ({JOURS_ACTIVITE_RECENTE} derniers jours)</div>
            <div className="carte-kpi__valeur">{utilisateursActifs}</div>
          </div>
        </div>
      </div>

      <div className="carte carte--graphique carte--graphique-activite">
        <div className="entete-carte-graphique">
          <h2>Inscriptions</h2>
          <div className="segmented-control">
            {(Object.keys(LIBELLES_GRANULARITE) as Granularite[]).map((g) => (
              <button
                key={g}
                type="button"
                className={`segmented-control__bouton${granularite === g ? " segmented-control__bouton--actif" : ""}`}
                onClick={() => setGranularite(g)}
              >
                {LIBELLES_GRANULARITE[g]}
              </button>
            ))}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={donneesInscriptions}>
            <defs>
              <linearGradient id="degrade-nouveaux-utilisateurs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COULEUR_NOUVEAUX} stopOpacity={0.35} />
                <stop offset="95%" stopColor={COULEUR_NOUVEAUX} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="degrade-cumule-utilisateurs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COULEUR_CUMULE} stopOpacity={0.35} />
                <stop offset="95%" stopColor={COULEUR_CUMULE} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={GRIS_GRILLE} />
            <XAxis dataKey="libelle" tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
            <YAxis yAxisId="nouveaux" tick={{ fontSize: 12 }} stroke={GRIS_AXE} allowDecimals={false} width={28} />
            <YAxis
              yAxisId="cumule"
              orientation="right"
              tick={{ fontSize: 12 }}
              stroke={GRIS_AXE}
              allowDecimals={false}
              width={28}
            />
            <Tooltip />
            <Legend />
            <Area
              yAxisId="nouveaux"
              type="monotone"
              dataKey="nouveaux"
              name="Nouveaux utilisateurs"
              stroke={COULEUR_NOUVEAUX}
              strokeWidth={2}
              fill="url(#degrade-nouveaux-utilisateurs)"
              dot={false}
              activeDot={{ r: 4 }}
            />
            <Area
              yAxisId="cumule"
              type="monotone"
              dataKey="cumule"
              name="Total cumulé"
              stroke={COULEUR_CUMULE}
              strokeWidth={2}
              fill="url(#degrade-cumule-utilisateurs)"
              dot={false}
              activeDot={{ r: 4 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
