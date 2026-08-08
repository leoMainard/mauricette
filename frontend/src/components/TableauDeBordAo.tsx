import { AlertTriangle, CheckCircle2, FileStack, FolderOpen, Loader2, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { obtenirVolumeDocumentsParJour } from "../api/statistiquesApi";
import type { AppelOffreAvecStatistiques, VolumeJour } from "../api/types";
import { cleSelonGranularite, genererPeriodes, LIBELLES_GRANULARITE } from "../utils/granularite";
import type { Granularite } from "../utils/granularite";
import { seuilAvancement } from "./BarreProgression";

interface Props {
  appelsOffre: AppelOffreAvecStatistiques[];
}

// Couleurs figées (et non `var(--...)`) : les attributs de présentation SVG rendus par
// recharts ne résolvent pas les custom properties CSS, contrairement au style en cascade.
// Valeurs reprises telles quelles de la palette définie dans `index.css`.
const COULEURS_STATUT: Record<string, string> = {
  brouillon: "#5c6c95",
  en_cours: "#133478",
  traite: "#009685",
  archive: "#d0d5e1",
  en_erreur: "#d1372a",
};

const LIBELLES_STATUT: Record<string, string> = {
  brouillon: "Brouillon",
  en_cours: "En cours",
  traite: "Traité",
  archive: "Archivé",
  en_erreur: "Erreur d'analyse",
};

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";
const COULEUR_AO = "#133478";
const COULEUR_DOCUMENTS = "#009685";

/** Tableau de bord (KPIs + graphiques) sur l'ensemble des AO, calculé côté client à
 * partir des données déjà chargées pour la liste (pas d'appel réseau supplémentaire,
 * à l'exception du volume journalier de documents analysés). */
export function TableauDeBordAo({ appelsOffre }: Props) {
  const [volumeJournalier, setVolumeJournalier] = useState<VolumeJour[]>([]);
  const [granularite, setGranularite] = useState<Granularite>("semaine");

  useEffect(() => {
    let annule = false;
    obtenirVolumeDocumentsParJour()
      .then((volumes) => {
        if (!annule) setVolumeJournalier(volumes);
      })
      .catch(() => {
        // Amélioration d'affichage : une erreur ici ne doit pas bloquer le reste du dashboard.
      });
    return () => {
      annule = true;
    };
  }, []);

  const stats = useMemo(() => {
    let enCours = 0;
    let traites = 0;
    let enErreur = 0;
    let sansReferentiel = 0;
    let documentsTotaux = 0;
    const repartition: Record<string, number> = {};
    let sommeCompletude = 0;
    let nombreAvecQuestions = 0;

    for (const ao of appelsOffre) {
      const cle = ao.en_erreur_analyse ? "en_erreur" : ao.appel_offre.statut;
      repartition[cle] = (repartition[cle] ?? 0) + 1;

      if (ao.en_erreur_analyse) enErreur += 1;
      else if (ao.appel_offre.statut === "en_cours") enCours += 1;
      else if (ao.appel_offre.statut === "traite") traites += 1;

      documentsTotaux += ao.nombre_documents;

      if (ao.questions_actives > 0) {
        sommeCompletude += ao.reponses_generees / ao.questions_actives;
        nombreAvecQuestions += 1;
      } else {
        sansReferentiel += 1;
      }
    }

    const completudeMoyenne =
      nombreAvecQuestions > 0 ? Math.round((sommeCompletude / nombreAvecQuestions) * 100) : null;

    const donneesRepartition = Object.entries(repartition).map(([statut, valeur]) => ({
      statut,
      libelle: LIBELLES_STATUT[statut] ?? statut,
      valeur,
    }));

    return {
      total: appelsOffre.length,
      enCours,
      traites,
      enErreur,
      sansReferentiel,
      documentsTotaux,
      completudeMoyenne,
      donneesRepartition,
    };
  }, [appelsOffre]);

  const donneesActivite = useMemo(() => {
    const periodes = genererPeriodes(granularite);
    const parCle = new Map(
      periodes.map((p) => [p.cle, { libelle: p.libelle, aoCreees: 0, documentsAnalyses: 0 }]),
    );

    for (const ao of appelsOffre) {
      const cle = cleSelonGranularite(new Date(ao.appel_offre.date_creation), granularite);
      const entree = parCle.get(cle);
      if (entree) entree.aoCreees += 1;
    }
    for (const volume of volumeJournalier) {
      const cle = cleSelonGranularite(new Date(volume.jour), granularite);
      const entree = parCle.get(cle);
      if (entree) entree.documentsAnalyses += volume.nombre;
    }

    return periodes.map((p) => parCle.get(p.cle)!);
  }, [appelsOffre, volumeJournalier, granularite]);

  return (
    <div className="tableau-de-bord">
      <div className="grille-kpi">
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <FolderOpen size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Total AO</div>
            <div className="carte-kpi__valeur">{stats.total}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--cyan">
            <Loader2 size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">En cours d'analyse</div>
            <div className="carte-kpi__valeur">{stats.enCours}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--vert">
            <CheckCircle2 size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Traités</div>
            <div className="carte-kpi__valeur">{stats.traites}</div>
          </div>
        </div>
        <div className={`carte-kpi${stats.enErreur > 0 ? " carte-kpi--alerte" : ""}`}>
          <div className="carte-kpi__icone carte-kpi__icone--erreur">
            <AlertTriangle size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">En erreur d'analyse</div>
            <div className="carte-kpi__valeur">{stats.enErreur}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--orange">
            <FileStack size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Documents totaux</div>
            <div className="carte-kpi__valeur">{stats.documentsTotaux}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <TrendingUp size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Complétude moyenne</div>
            <div
              className={`carte-kpi__valeur${
                stats.completudeMoyenne !== null
                  ? ` carte-kpi__valeur--${seuilAvancement(stats.completudeMoyenne)}`
                  : ""
              }`}
            >
              {stats.completudeMoyenne !== null ? `${stats.completudeMoyenne}%` : "—"}
            </div>
          </div>
        </div>
      </div>

      {stats.sansReferentiel > 0 && (
        <p className="texte-discret note-dashboard">
          <AlertTriangle size={13} /> {stats.sansReferentiel} AO sans référentiel attaché — aucune
          analyse ne peut démarrer tant qu'aucun référentiel n'est rattaché.
        </p>
      )}

      <div className="grille-graphiques">
        <div className="carte carte--graphique carte--graphique-donut">
          <h2>Répartition par statut</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={stats.donneesRepartition}
                dataKey="valeur"
                nameKey="libelle"
                innerRadius={45}
                outerRadius={70}
                paddingAngle={2}
              >
                {stats.donneesRepartition.map((entree) => (
                  <Cell key={entree.statut} fill={COULEURS_STATUT[entree.statut] ?? "#5c6c95"} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="carte carte--graphique carte--graphique-activite">
          <div className="entete-carte-graphique">
            <h2>Activité</h2>
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
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={donneesActivite}>
              <defs>
                <linearGradient id="degrade-ao" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COULEUR_AO} stopOpacity={0.35} />
                  <stop offset="95%" stopColor={COULEUR_AO} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="degrade-documents" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COULEUR_DOCUMENTS} stopOpacity={0.35} />
                  <stop offset="95%" stopColor={COULEUR_DOCUMENTS} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={GRIS_GRILLE} />
              <XAxis dataKey="libelle" tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <YAxis
                yAxisId="ao"
                tick={{ fontSize: 12 }}
                stroke={GRIS_AXE}
                allowDecimals={false}
                width={28}
              />
              <YAxis
                yAxisId="documents"
                orientation="right"
                tick={{ fontSize: 12 }}
                stroke={GRIS_AXE}
                allowDecimals={false}
                width={28}
              />
              <Tooltip />
              <Legend />
              <Area
                yAxisId="ao"
                type="monotone"
                dataKey="aoCreees"
                name="AO créés"
                stroke={COULEUR_AO}
                strokeWidth={2}
                fill="url(#degrade-ao)"
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Area
                yAxisId="documents"
                type="monotone"
                dataKey="documentsAnalyses"
                name="Documents analysés"
                stroke={COULEUR_DOCUMENTS}
                strokeWidth={2}
                fill="url(#degrade-documents)"
                dot={false}
                activeDot={{ r: 4 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
