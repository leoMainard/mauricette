import { BookOpen, Cpu, Gauge, LayoutGrid, ThumbsUp, TrendingUp, Trophy, Users, UsersRound, UserX } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  listerTousLesAppelsOffre,
  listerTousLesReferentiels,
  obtenirStatistiquesFeedback,
  obtenirStatistiquesPipeline,
  obtenirStatistiquesQualite,
} from "../api/adminApi";
import { ErreurApi } from "../api/client";
import type {
  AppelOffreAvecStatistiques,
  GroupeUtilisateur,
  ReferentielAvecStatistiques,
  StatistiquesFeedback,
  StatistiquesPipeline,
  StatistiquesQualite,
  Utilisateur,
} from "../api/types";
import { listerGroupes, listerUtilisateurs } from "../api/utilisateurApi";
import { OngletAdoption } from "../components/admin/OngletAdoption";
import { OngletClassements } from "../components/admin/OngletClassements";
import { OngletFeedback } from "../components/admin/OngletFeedback";
import { OngletPipelineRag } from "../components/admin/OngletPipelineRag";
import { OngletQualiteIA } from "../components/admin/OngletQualiteIA";
import { Layout } from "../components/Layout";
import { TableauDeBordAo } from "../components/TableauDeBordAo";

type Onglet = "vue-ensemble" | "pipeline" | "qualite" | "adoption" | "classements" | "feedback";

const ONGLETS: { id: Onglet; label: string; Icone: typeof LayoutGrid }[] = [
  { id: "vue-ensemble", label: "Vue d'ensemble", Icone: LayoutGrid },
  { id: "pipeline", label: "Pipeline RAG", Icone: Cpu },
  { id: "qualite", label: "Qualité IA", Icone: Gauge },
  { id: "adoption", label: "Adoption", Icone: TrendingUp },
  { id: "classements", label: "Classements", Icone: Trophy },
  { id: "feedback", label: "Feedback", Icone: ThumbsUp },
];

/** Tableau de bord admin : vue globale de l'application, tous utilisateurs et groupes confondus. */
export function PageTableauDeBordAdmin() {
  const [ongletActif, setOngletActif] = useState<Onglet>("vue-ensemble");

  const [appelsOffre, setAppelsOffre] = useState<AppelOffreAvecStatistiques[]>([]);
  const [referentiels, setReferentiels] = useState<ReferentielAvecStatistiques[]>([]);
  const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
  const [groupes, setGroupes] = useState<GroupeUtilisateur[]>([]);
  const [feedback, setFeedback] = useState<StatistiquesFeedback | null>(null);
  const [pipeline, setPipeline] = useState<StatistiquesPipeline | null>(null);
  const [qualite, setQualite] = useState<StatistiquesQualite | null>(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      listerTousLesAppelsOffre(),
      listerTousLesReferentiels(),
      listerUtilisateurs(),
      listerGroupes(),
      obtenirStatistiquesFeedback(),
      obtenirStatistiquesPipeline(),
      obtenirStatistiquesQualite(),
    ])
      .then(([ao, refs, users, grps, fb, pl, ql]) => {
        setAppelsOffre(ao);
        setReferentiels(refs);
        setUtilisateurs(users);
        setGroupes(grps);
        setFeedback(fb);
        setPipeline(pl);
        setQualite(ql);
      })
      .catch((e) => setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement."))
      .finally(() => setChargement(false));
  }, []);

  const utilisateursSansGroupe = useMemo(
    () => utilisateurs.filter((u) => u.groupe_id === null).length,
    [utilisateurs],
  );

  if (chargement) {
    return (
      <Layout>
        <p className="texte-discret">Chargement...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      {erreur && <p className="message-erreur">{erreur}</p>}
      <h1>Tableau de bord admin</h1>
      <p className="texte-discret">
        Vue globale de l'application, tous utilisateurs et groupes confondus.
      </p>

      <div className="barre-onglets">
        {ONGLETS.map(({ id, label, Icone }) => (
          <button
            key={id}
            type="button"
            className={`onglet${ongletActif === id ? " onglet--actif" : ""}`}
            onClick={() => setOngletActif(id)}
          >
            <Icone size={16} />
            {label}
          </button>
        ))}
      </div>

      {ongletActif === "vue-ensemble" && (
        <>
          <TableauDeBordAo appelsOffre={appelsOffre} />

          <h2>Utilisateurs, groupes et référentiels</h2>
          <div className="grille-kpi">
            <div className="carte-kpi">
              <div className="carte-kpi__icone carte-kpi__icone--marine">
                <Users size={18} />
              </div>
              <div>
                <div className="carte-kpi__libelle">Utilisateurs</div>
                <div className="carte-kpi__valeur">{utilisateurs.length}</div>
              </div>
            </div>
            <div className="carte-kpi">
              <div className="carte-kpi__icone carte-kpi__icone--cyan">
                <UsersRound size={18} />
              </div>
              <div>
                <div className="carte-kpi__libelle">Groupes</div>
                <div className="carte-kpi__valeur">{groupes.length}</div>
              </div>
            </div>
            <div className="carte-kpi">
              <div className="carte-kpi__icone carte-kpi__icone--vert">
                <BookOpen size={18} />
              </div>
              <div>
                <div className="carte-kpi__libelle">Référentiels</div>
                <div className="carte-kpi__valeur">{referentiels.length}</div>
              </div>
            </div>
            <div className={`carte-kpi${utilisateursSansGroupe > 0 ? " carte-kpi--alerte" : ""}`}>
              <div className="carte-kpi__icone carte-kpi__icone--orange">
                <UserX size={18} />
              </div>
              <div>
                <div className="carte-kpi__libelle">Utilisateurs sans groupe</div>
                <div className="carte-kpi__valeur">{utilisateursSansGroupe}</div>
              </div>
            </div>
          </div>
        </>
      )}
      {ongletActif === "pipeline" && pipeline && <OngletPipelineRag pipeline={pipeline} />}
      {ongletActif === "qualite" && qualite && (
        <OngletQualiteIA qualite={qualite} referentiels={referentiels} />
      )}
      {ongletActif === "adoption" && (
        <OngletAdoption utilisateurs={utilisateurs} appelsOffre={appelsOffre} />
      )}
      {ongletActif === "classements" && (
        <OngletClassements
          appelsOffre={appelsOffre}
          referentiels={referentiels}
          utilisateurs={utilisateurs}
          groupes={groupes}
        />
      )}
      {ongletActif === "feedback" && feedback && (
        <OngletFeedback
          feedback={feedback}
          referentiels={referentiels}
          totalAppelsOffre={appelsOffre.length}
        />
      )}
    </Layout>
  );
}
