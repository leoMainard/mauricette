import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type {
  AppelOffreAvecStatistiques,
  GroupeUtilisateur,
  ReferentielAvecStatistiques,
  Utilisateur,
} from "../../api/types";

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";
const MARINE = "#133478";
const VERT = "#009685";
const CYAN_MID = "#31c6f5";

const NOMBRE_LIGNES_AFFICHEES = 10;

interface Props {
  appelsOffre: AppelOffreAvecStatistiques[];
  referentiels: ReferentielAvecStatistiques[];
  utilisateurs: Utilisateur[];
  groupes: GroupeUtilisateur[];
}

/** Onglet admin : classements utilisateurs/groupes/référentiels par activité. */
export function OngletClassements({ appelsOffre, referentiels, utilisateurs, groupes }: Props) {
  const nomParUtilisateur = useMemo(
    () => new Map(utilisateurs.map((u) => [u.id, u.nom])),
    [utilisateurs],
  );
  const groupeParUtilisateur = useMemo(
    () => new Map(utilisateurs.map((u) => [u.id, u.groupe_id])),
    [utilisateurs],
  );

  const parUtilisateur = useMemo(() => {
    const stats = new Map<string, { nom: string; ao: number; documents: number }>();
    for (const { appel_offre, nombre_documents } of appelsOffre) {
      const id = appel_offre.cree_par_id;
      if (!id) continue;
      const nom = nomParUtilisateur.get(id) ?? appel_offre.cree_par;
      const entree = stats.get(id) ?? { nom, ao: 0, documents: 0 };
      entree.ao += 1;
      entree.documents += nombre_documents;
      stats.set(id, entree);
    }
    return Array.from(stats.values())
      .sort((a, b) => b.ao - a.ao)
      .slice(0, NOMBRE_LIGNES_AFFICHEES);
  }, [appelsOffre, nomParUtilisateur]);

  const parGroupe = useMemo(() => {
    const stats = new Map<string, number>();
    for (const { appel_offre } of appelsOffre) {
      const id = appel_offre.cree_par_id;
      if (!id) continue;
      const groupeId = groupeParUtilisateur.get(id);
      if (!groupeId) continue;
      stats.set(groupeId, (stats.get(groupeId) ?? 0) + 1);
    }
    return groupes
      .map((groupe) => ({ nom: groupe.nom, ao: stats.get(groupe.id) ?? 0 }))
      .filter((g) => g.ao > 0)
      .sort((a, b) => b.ao - a.ao)
      .slice(0, NOMBRE_LIGNES_AFFICHEES);
  }, [appelsOffre, groupes, groupeParUtilisateur]);

  const referentielsUtilises = useMemo(
    () =>
      referentiels
        .map((r) => ({ nom: r.referentiel.nom, ao: r.nombre_ao_concernes }))
        .filter((r) => r.ao > 0)
        .sort((a, b) => b.ao - a.ao)
        .slice(0, NOMBRE_LIGNES_AFFICHEES),
    [referentiels],
  );

  return (
    <>
      {parUtilisateur.length > 0 && (
        <div className="carte carte--graphique">
          <h2>Activité par utilisateur</h2>
          <ResponsiveContainer width="100%" height={Math.max(200, parUtilisateur.length * 36)}>
            <BarChart data={parUtilisateur} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <YAxis type="category" dataKey="nom" width={110} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <Tooltip />
              <Bar dataKey="ao" name="AO déposés" fill={MARINE} radius={[0, 4, 4, 0]} />
              <Bar dataKey="documents" name="Documents déposés" fill={CYAN_MID} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grille-graphiques-egale">
        {parGroupe.length > 0 && (
          <div className="carte carte--graphique">
            <h2>AO par groupe</h2>
            <ResponsiveContainer width="100%" height={Math.max(160, parGroupe.length * 40)}>
              <BarChart data={parGroupe} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
                <YAxis type="category" dataKey="nom" width={110} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
                <Tooltip />
                <Bar dataKey="ao" name="AO" fill={MARINE} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {referentielsUtilises.length > 0 && (
          <div className="carte carte--graphique">
            <h2>Référentiels les plus utilisés</h2>
            <ResponsiveContainer width="100%" height={Math.max(160, referentielsUtilises.length * 40)}>
              <BarChart data={referentielsUtilises} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
                <YAxis type="category" dataKey="nom" width={110} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
                <Tooltip />
                <Bar dataKey="ao" name="AO concernés" fill={VERT} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </>
  );
}
