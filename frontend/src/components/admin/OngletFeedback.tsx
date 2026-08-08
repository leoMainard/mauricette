import { PieChart as PieChartIcon, ThumbsDown, ThumbsUp } from "lucide-react";
import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
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
import type { FeedbackReponseDetaille, ReferentielAvecStatistiques, StatistiquesFeedback } from "../../api/types";
import type { Granularite } from "../../utils/granularite";
import { cleSelonGranularite, genererPeriodes, LIBELLES_GRANULARITE } from "../../utils/granularite";
import { LIBELLES_TYPE_ERREUR } from "../WidgetFeedbackReponse";

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";
const VERT = "#009685";
const ERREUR = "#d1372a";
const ORANGE = "#f8a909";

const NOMBRE_REFERENTIELS_AFFICHES = 10;

interface Props {
  feedback: StatistiquesFeedback;
  referentiels: ReferentielAvecStatistiques[];
  totalAppelsOffre: number;
}

function AvisIcone({ avis }: { avis: FeedbackReponseDetaille["avis"] }) {
  if (avis === "positif") return <ThumbsUp size={15} color={VERT} aria-label="Positif" />;
  if (avis === "negatif") return <ThumbsDown size={15} color={ERREUR} aria-label="Négatif" />;
  return <span className="texte-discret">—</span>;
}

const donneesAvis = (parAvis: Record<string, number>) =>
  [
    { avis: "positif", libelle: "Positif", valeur: parAvis.positif ?? 0 },
    { avis: "negatif", libelle: "Négatif", valeur: parAvis.negatif ?? 0 },
  ].filter((d) => d.valeur > 0);

/** Onglet admin : feedback approfondi (évolution dans le temps, couverture,
 * référentiels concentrant le plus de retours négatifs). */
export function OngletFeedback({ feedback, referentiels, totalAppelsOffre }: Props) {
  const [granularite, setGranularite] = useState<Granularite>("semaine");
  const [referentielFiltre, setReferentielFiltre] = useState("");
  const [questionFiltre, setQuestionFiltre] = useState("");

  function changerReferentielFiltre(id: string) {
    setReferentielFiltre(id);
    setQuestionFiltre("");
  }

  const nomParReferentiel = useMemo(
    () => new Map(referentiels.map((r) => [r.referentiel.id, r.referentiel.nom])),
    [referentiels],
  );

  const tauxCouverture =
    totalAppelsOffre > 0
      ? Math.round(
          (feedback.general_bruts.filter((f) => f.avis !== null).length / totalAppelsOffre) * 100,
        )
      : null;

  const evolutionAvis = useMemo(() => {
    const periodes = genererPeriodes(granularite);
    const parCle = new Map(periodes.map((p) => [p.cle, { libelle: p.libelle, positif: 0, negatif: 0 }]));
    for (const f of feedback.general_bruts) {
      if (!f.avis) continue;
      const cle = cleSelonGranularite(new Date(f.date_creation), granularite);
      const entree = parCle.get(cle);
      if (entree) entree[f.avis as "positif" | "negatif"] += 1;
    }
    return periodes.map((p) => parCle.get(p.cle)!);
  }, [feedback.general_bruts, granularite]);

  const donneesTypeErreur = Object.entries(feedback.reponse_par_type_erreur).map(([type, nombre]) => ({
    type,
    libelle: LIBELLES_TYPE_ERREUR[type as keyof typeof LIBELLES_TYPE_ERREUR] ?? type,
    nombre,
  }));

  const referentielsNegatifs = useMemo(
    () =>
      Object.entries(feedback.reponse_negatifs_par_referentiel)
        .map(([id, nombre]) => ({ nom: nomParReferentiel.get(id) ?? id, nombre }))
        .sort((a, b) => b.nombre - a.nombre)
        .slice(0, NOMBRE_REFERENTIELS_AFFICHES),
    [feedback.reponse_negatifs_par_referentiel, nomParReferentiel],
  );

  const parQuestion = useMemo(() => {
    const map = new Map<
      string,
      { referentielNom: string; question: string; positifs: number; negatifs: number }
    >();
    for (const f of feedback.reponse_detailles) {
      if (!f.avis) continue;
      const entree = map.get(f.question_referentiel_id) ?? {
        referentielNom: f.referentiel_nom,
        question: f.question,
        positifs: 0,
        negatifs: 0,
      };
      if (f.avis === "positif") entree.positifs += 1;
      else entree.negatifs += 1;
      map.set(f.question_referentiel_id, entree);
    }
    return Array.from(map.values()).sort(
      (a, b) => b.negatifs - a.negatifs || b.positifs + b.negatifs - (a.positifs + a.negatifs),
    );
  }, [feedback.reponse_detailles]);

  const referentielsDisponibles = useMemo(() => {
    const map = new Map<string, string>();
    for (const f of feedback.reponse_detailles) map.set(f.referentiel_id, f.referentiel_nom);
    return Array.from(map.entries())
      .map(([id, nom]) => ({ id, nom }))
      .sort((a, b) => a.nom.localeCompare(b.nom));
  }, [feedback.reponse_detailles]);

  const questionsDisponibles = useMemo(() => {
    const map = new Map<string, string>();
    for (const f of feedback.reponse_detailles) {
      if (referentielFiltre && f.referentiel_id !== referentielFiltre) continue;
      map.set(f.question_referentiel_id, f.question);
    }
    return Array.from(map.entries())
      .map(([id, question]) => ({ id, question }))
      .sort((a, b) => a.question.localeCompare(b.question));
  }, [feedback.reponse_detailles, referentielFiltre]);

  const detaillesFiltres = useMemo(
    () =>
      feedback.reponse_detailles
        .filter((f) => !referentielFiltre || f.referentiel_id === referentielFiltre)
        .filter((f) => !questionFiltre || f.question_referentiel_id === questionFiltre)
        .sort((a, b) => b.date_creation.localeCompare(a.date_creation)),
    [feedback.reponse_detailles, referentielFiltre, questionFiltre],
  );

  return (
    <>
      <div className="grille-kpi">
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <PieChartIcon size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Taux de couverture (avis général)</div>
            <div className="carte-kpi__valeur">{tauxCouverture !== null ? `${tauxCouverture}%` : "—"}</div>
          </div>
        </div>
      </div>

      <div className="carte carte--graphique carte--graphique-activite">
        <div className="entete-carte-graphique">
          <h2>Évolution de l'avis général</h2>
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
          <AreaChart data={evolutionAvis}>
            <defs>
              <linearGradient id="degrade-avis-positif" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={VERT} stopOpacity={0.35} />
                <stop offset="95%" stopColor={VERT} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="degrade-avis-negatif" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={ERREUR} stopOpacity={0.35} />
                <stop offset="95%" stopColor={ERREUR} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={GRIS_GRILLE} />
            <XAxis dataKey="libelle" tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} width={28} />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="positif" name="Positif" stroke={VERT} strokeWidth={2} fill="url(#degrade-avis-positif)" dot={false} activeDot={{ r: 4 }} />
            <Area type="monotone" dataKey="negatif" name="Négatif" stroke={ERREUR} strokeWidth={2} fill="url(#degrade-avis-negatif)" dot={false} activeDot={{ r: 4 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grille-graphiques-egale">
        <div className="carte carte--graphique carte--graphique-donut">
          <h2>Avis général</h2>
          {donneesAvis(feedback.general_par_avis).length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={donneesAvis(feedback.general_par_avis)} dataKey="valeur" nameKey="libelle" innerRadius={40} outerRadius={65} paddingAngle={2}>
                  {donneesAvis(feedback.general_par_avis).map((entree) => (
                    <Cell key={entree.avis} fill={entree.avis === "positif" ? VERT : ERREUR} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="texte-discret">Aucun avis général pour le moment.</p>
          )}
        </div>
        <div className="carte carte--graphique carte--graphique-donut">
          <h2>Avis par réponse</h2>
          {donneesAvis(feedback.reponse_par_avis).length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={donneesAvis(feedback.reponse_par_avis)} dataKey="valeur" nameKey="libelle" innerRadius={40} outerRadius={65} paddingAngle={2}>
                  {donneesAvis(feedback.reponse_par_avis).map((entree) => (
                    <Cell key={entree.avis} fill={entree.avis === "positif" ? VERT : ERREUR} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="texte-discret">Aucun avis par réponse pour le moment.</p>
          )}
        </div>
      </div>

      {donneesTypeErreur.length > 0 && (
        <div className="carte carte--graphique">
          <h2>Types d'erreur signalés</h2>
          <ResponsiveContainer width="100%" height={Math.max(160, donneesTypeErreur.length * 36)}>
            <BarChart data={donneesTypeErreur} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <YAxis type="category" dataKey="libelle" width={170} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <Tooltip />
              <Bar dataKey="nombre" name="Signalements" fill={ERREUR} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {referentielsNegatifs.length > 0 && (
        <div className="carte carte--graphique">
          <h2>Référentiels avec le plus de retours négatifs</h2>
          <ResponsiveContainer width="100%" height={Math.max(160, referentielsNegatifs.length * 36)}>
            <BarChart data={referentielsNegatifs} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <YAxis type="category" dataKey="nom" width={170} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
              <Tooltip />
              <Bar dataKey="nombre" name="Retours négatifs" fill={ORANGE} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {parQuestion.length > 0 && (
        <div className="carte">
          <h2>Analyse par question</h2>
          <div style={{ overflowX: "auto" }}>
            <table className="table-documents">
              <thead>
                <tr>
                  <th>Référentiel</th>
                  <th>Question</th>
                  <th>Positifs</th>
                  <th>Négatifs</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {parQuestion.map((q) => (
                  <tr key={`${q.referentielNom}-${q.question}`}>
                    <td>{q.referentielNom}</td>
                    <td>{q.question}</td>
                    <td>{q.positifs}</td>
                    <td>{q.negatifs}</td>
                    <td>{q.positifs + q.negatifs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {feedback.reponse_detailles.length > 0 && (
        <div className="carte">
          <div className="entete-carte-tableau">
            <h2>Feedbacks détaillés</h2>
            <div className="filtres-tableau-ao">
              <select
                value={referentielFiltre}
                onChange={(e) => changerReferentielFiltre(e.target.value)}
                aria-label="Filtrer par référentiel"
              >
                <option value="">Tous les référentiels</option>
                {referentielsDisponibles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.nom}
                  </option>
                ))}
              </select>
              <select
                value={questionFiltre}
                onChange={(e) => setQuestionFiltre(e.target.value)}
                aria-label="Filtrer par question"
              >
                <option value="">Toutes les questions</option>
                {questionsDisponibles.map((q) => (
                  <option key={q.id} value={q.id}>
                    {q.question}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {detaillesFiltres.length === 0 ? (
            <p className="texte-discret texte-vide-tableau">Aucun feedback pour ce filtre.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="table-documents">
                <thead>
                  <tr>
                    <th>AO</th>
                    <th>Question</th>
                    <th>Avis</th>
                    <th>Commentaire</th>
                    <th>Source attendue</th>
                    <th>Citation attendue</th>
                    <th>Type d'erreur</th>
                    <th>Précisions</th>
                  </tr>
                </thead>
                <tbody>
                  {detaillesFiltres.map((f) => (
                    <tr key={f.id}>
                      <td>{f.appel_offre_nom}</td>
                      <td>{f.question}</td>
                      <td>
                        <AvisIcone avis={f.avis} />
                      </td>
                      <td>{f.commentaire ?? "—"}</td>
                      <td>{f.source_attendue ?? "—"}</td>
                      <td>{f.citation_attendue ?? "—"}</td>
                      <td>{f.type_erreur ? LIBELLES_TYPE_ERREUR[f.type_erreur] : "—"}</td>
                      <td>{f.details_erreur ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </>
  );
}
