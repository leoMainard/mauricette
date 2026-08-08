import { AlertOctagon, Clock } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { StatistiquesPipeline } from "../../api/types";

const GRIS_AXE = "#5c6c95";
const GRIS_GRILLE = "#d0d5e1";

const LIBELLES_ETAPE: Record<string, string> = {
  extraction: "Extraction",
  decoupage: "Découpage",
  embedding: "Embedding",
};

const LIBELLES_STATUT: Record<string, string> = {
  en_attente: "En attente",
  en_cours: "En cours",
  reussi: "Réussi",
  echec: "Échec",
};

const COULEURS_STATUT: Record<string, string> = {
  en_attente: "#d0d5e1",
  en_cours: "#31c6f5",
  reussi: "#009685",
  echec: "#d1372a",
};

const LIBELLES_TYPE_TACHE: Record<string, string> = {
  extraction_document: "Extraction document",
  decoupage_document: "Découpage document",
  embedding_document: "Embedding document",
  regeneration_reponses_ao: "Régénération réponses AO",
};

function formaterDuree(secondes: number): string {
  if (secondes < 60) return `${Math.round(secondes)} s`;
  const minutes = Math.round(secondes / 60);
  return `${minutes} min`;
}

interface Props {
  pipeline: StatistiquesPipeline;
}

/** Onglet admin : santé du pipeline RAG (extraction/découpage/embedding) et de la
 * file d'attente de traitement asynchrone. */
export function OngletPipelineRag({ pipeline }: Props) {
  const tachesParType = Object.entries(pipeline.taches_par_type).map(([type, parStatut]) => ({
    type,
    libelle: LIBELLES_TYPE_TACHE[type] ?? type,
    ...parStatut,
  }));

  return (
    <>
      <div className="grille-kpi">
        <div className="carte-kpi">
          <div className="carte-kpi__icone carte-kpi__icone--marine">
            <Clock size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Durée moyenne de traitement</div>
            <div className="carte-kpi__valeur">
              {pipeline.duree_moyenne_traitement_secondes !== null
                ? formaterDuree(pipeline.duree_moyenne_traitement_secondes)
                : "—"}
            </div>
          </div>
        </div>
        <div className={`carte-kpi${pipeline.taches_echecs_definitifs > 0 ? " carte-kpi--alerte" : ""}`}>
          <div className="carte-kpi__icone carte-kpi__icone--erreur">
            <AlertOctagon size={18} />
          </div>
          <div>
            <div className="carte-kpi__libelle">Tâches en échec définitif</div>
            <div className="carte-kpi__valeur">{pipeline.taches_echecs_definitifs}</div>
          </div>
        </div>
      </div>

      <div className="grille-etapes-pipeline">
        {(["extraction", "decoupage", "embedding"] as const).map((etape) => {
          const parStatut = pipeline.documents_par_etape[etape] ?? {};
          const donnees = Object.entries(parStatut).map(([statut, valeur]) => ({
            statut,
            libelle: LIBELLES_STATUT[statut] ?? statut,
            valeur,
          }));
          return (
            <div key={etape} className="carte carte--graphique">
              <h2>{LIBELLES_ETAPE[etape]}</h2>
              {donnees.length > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={donnees} dataKey="valeur" nameKey="libelle" innerRadius={38} outerRadius={60} paddingAngle={2}>
                      {donnees.map((entree) => (
                        <Cell key={entree.statut} fill={COULEURS_STATUT[entree.statut] ?? GRIS_AXE} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="texte-discret">Aucune donnée.</p>
              )}
            </div>
          );
        })}
      </div>

      <div className="carte carte--graphique">
        <h2>Tâches de traitement par type</h2>
        <ResponsiveContainer width="100%" height={Math.max(160, tachesParType.length * 50)}>
          <BarChart data={tachesParType} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={GRIS_GRILLE} />
            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
            <YAxis type="category" dataKey="libelle" width={160} tick={{ fontSize: 12 }} stroke={GRIS_AXE} />
            <Tooltip />
            <Legend />
            <Bar dataKey="reussi" name="Réussi" stackId="tache" fill={COULEURS_STATUT.reussi} />
            <Bar dataKey="en_cours" name="En cours" stackId="tache" fill={COULEURS_STATUT.en_cours} />
            <Bar dataKey="en_attente" name="En attente" stackId="tache" fill={COULEURS_STATUT.en_attente} />
            <Bar dataKey="echec" name="Échec" stackId="tache" fill={COULEURS_STATUT.echec} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
