import { Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listerAppelsOffre, supprimerAppelOffre } from "../api/appelsOffreApi";
import { ErreurApi } from "../api/client";
import type { AppelOffreAvecStatistiques, StatutAppelOffre } from "../api/types";
import { Badge } from "../components/Badge";
import { BarreProgression } from "../components/BarreProgression";
import { Layout } from "../components/Layout";
import { ModaleConfirmation } from "../components/ModaleConfirmation";
import { TableauDeBordAo } from "../components/TableauDeBordAo";

const LIBELLES_STATUT: Record<StatutAppelOffre, string> = {
  brouillon: "Brouillon",
  en_cours: "En cours",
  traite: "Traité",
  archive: "Archivé",
};

const OPTIONS_STATUT: { valeur: string; libelle: string }[] = [
  { valeur: "tous", libelle: "Tous les statuts" },
  { valeur: "brouillon", libelle: "Brouillon" },
  { valeur: "en_cours", libelle: "En cours" },
  { valeur: "traite", libelle: "Traité" },
  { valeur: "archive", libelle: "Archivé" },
  { valeur: "en_erreur", libelle: "Erreur d'analyse" },
];

const OPTIONS_PERIODE: { valeur: string; libelle: string; jours: number | null }[] = [
  { valeur: "tous", libelle: "Toutes les dates", jours: null },
  { valeur: "7j", libelle: "7 derniers jours", jours: 7 },
  { valeur: "30j", libelle: "30 derniers jours", jours: 30 },
  { valeur: "90j", libelle: "90 derniers jours", jours: 90 },
];

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

/** Page d'accueil : tableau de bord + liste des Appels d'Offres, avec recherche et filtres. */
export function PageListeAppelsOffre() {
  const navigate = useNavigate();
  const [appelsOffre, setAppelsOffre] = useState<AppelOffreAvecStatistiques[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [aoASupprimer, setAoASupprimer] = useState<AppelOffreAvecStatistiques | null>(null);
  const [suppressionEnCours, setSuppressionEnCours] = useState(false);
  const [erreurSuppression, setErreurSuppression] = useState<string | null>(null);

  const [recherche, setRecherche] = useState("");
  const [filtreStatut, setFiltreStatut] = useState("tous");
  const [filtrePeriode, setFiltrePeriode] = useState("tous");

  // Chargé une seule fois : le tableau de bord porte sur l'ensemble du portefeuille,
  // et la recherche/les filtres ci-dessous s'appliquent ensuite côté client, sans
  // affecter les KPIs/graphiques (qui restent toujours une vue d'ensemble complète).
  useEffect(() => {
    let annule = false;
    setChargement(true);

    listerAppelsOffre()
      .then((resultats) => {
        if (!annule) setAppelsOffre(resultats);
      })
      .catch((e) => {
        if (!annule) setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement");
      })
      .finally(() => {
        if (!annule) setChargement(false);
      });

    return () => {
      annule = true;
    };
  }, []);

  const appelsOffreFiltres = useMemo(() => {
    const rechercheNormalisee = recherche.trim().toLowerCase();
    const periode = OPTIONS_PERIODE.find((p) => p.valeur === filtrePeriode);
    const limiteDate =
      periode?.jours != null
        ? new Date(Date.now() - periode.jours * 24 * 60 * 60 * 1000)
        : null;

    return appelsOffre.filter((ao) => {
      if (rechercheNormalisee && !ao.appel_offre.nom.toLowerCase().includes(rechercheNormalisee)) {
        return false;
      }
      if (filtreStatut !== "tous") {
        const statutEffectif = ao.en_erreur_analyse ? "en_erreur" : ao.appel_offre.statut;
        if (statutEffectif !== filtreStatut) return false;
      }
      if (limiteDate && new Date(ao.appel_offre.date_creation) < limiteDate) {
        return false;
      }
      return true;
    });
  }, [appelsOffre, recherche, filtreStatut, filtrePeriode]);

  async function confirmerSuppression() {
    if (!aoASupprimer) return;
    setSuppressionEnCours(true);
    setErreurSuppression(null);
    try {
      await supprimerAppelOffre(aoASupprimer.appel_offre.id);
      setAppelsOffre((precedent) =>
        precedent.filter((ao) => ao.appel_offre.id !== aoASupprimer.appel_offre.id),
      );
      setAoASupprimer(null);
    } catch (e) {
      setErreurSuppression(
        e instanceof ErreurApi ? e.message : "Erreur lors de la suppression de l'Appel d'Offres.",
      );
    } finally {
      setSuppressionEnCours(false);
    }
  }

  return (
    <Layout pleineLargeur>
      <div className="entete-page">
        <h1>Mes Appels d'Offres</h1>
        <p className="texte-discret">
          {appelsOffre.length} dossier{appelsOffre.length > 1 ? "s" : ""} · dépose, analyse et suis tes AO.
        </p>
      </div>

      {erreur && <p className="message-erreur">{erreur}</p>}

      {!chargement && appelsOffre.length > 0 && <TableauDeBordAo appelsOffre={appelsOffre} />}

      {chargement ? (
        <p className="texte-discret">Chargement...</p>
      ) : appelsOffre.length === 0 ? (
        <p className="texte-discret">Aucun Appel d'Offres pour le moment.</p>
      ) : (
        <div className="carte carte--tableau">
          <div className="entete-carte-tableau">
            <div>
              <h2>Tous les Appels d'Offres</h2>
              <span className="texte-discret">
                {appelsOffreFiltres.length} résultat{appelsOffreFiltres.length > 1 ? "s" : ""}
              </span>
            </div>
            <div className="filtres-tableau-ao">
              <input
                type="search"
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                placeholder="Rechercher un Appel d'Offres..."
                aria-label="Rechercher un Appel d'Offres par nom"
                className="champ-recherche"
              />
              <select
                value={filtreStatut}
                onChange={(e) => setFiltreStatut(e.target.value)}
                aria-label="Filtrer par statut"
              >
                {OPTIONS_STATUT.map((option) => (
                  <option key={option.valeur} value={option.valeur}>
                    {option.libelle}
                  </option>
                ))}
              </select>
              <select
                value={filtrePeriode}
                onChange={(e) => setFiltrePeriode(e.target.value)}
                aria-label="Filtrer par date de création"
              >
                {OPTIONS_PERIODE.map((option) => (
                  <option key={option.valeur} value={option.valeur}>
                    {option.libelle}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {appelsOffreFiltres.length === 0 ? (
            <p className="texte-discret texte-vide-tableau">
              Aucun Appel d'Offres ne correspond à ces critères.
            </p>
          ) : (
            <div className="tableau-defilant">
              <table className="table-documents">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Statut</th>
                    <th>Analyse</th>
                    <th>Créé par</th>
                    <th>Créé le</th>
                    <th>Documents</th>
                    <th>Taille</th>
                    <th aria-label="Actions" />
                  </tr>
                </thead>
                <tbody>
                  {appelsOffreFiltres.map((ao) => {
                    const {
                      appel_offre,
                      nombre_documents,
                      taille_totale_octets,
                      en_erreur_analyse,
                      questions_actives,
                      reponses_generees,
                    } = ao;
                    const pourcentageAnalyse =
                      questions_actives > 0
                        ? Math.round((reponses_generees / questions_actives) * 100)
                        : null;
                    return (
                      <tr
                        key={appel_offre.id}
                        className="ligne-cliquable"
                        tabIndex={0}
                        onClick={() => navigate(`/appels-offre/${appel_offre.id}`)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") navigate(`/appels-offre/${appel_offre.id}`);
                        }}
                      >
                        <td className="cellule-nom-ao">{appel_offre.nom}</td>
                        <td>
                          {en_erreur_analyse ? (
                            <Badge statut="en_erreur" libelle="Erreur d'analyse" />
                          ) : (
                            <Badge
                              statut={appel_offre.statut}
                              libelle={LIBELLES_STATUT[appel_offre.statut]}
                            />
                          )}
                        </td>
                        <td>
                          <BarreProgression pourcentage={pourcentageAnalyse} />
                        </td>
                        <td>{appel_offre.cree_par}</td>
                        <td>{formaterDate(appel_offre.date_creation)}</td>
                        <td>{nombre_documents}</td>
                        <td>{formaterTaille(taille_totale_octets)}</td>
                        <td>
                          <button
                            type="button"
                            className="bouton-icone bouton-icone--annuler"
                            onClick={(e) => {
                              e.stopPropagation();
                              setErreurSuppression(null);
                              setAoASupprimer(ao);
                            }}
                            title="Supprimer"
                            aria-label={`Supprimer ${appel_offre.nom}`}
                          >
                            <Trash2 size={15} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {aoASupprimer && (
        <ModaleConfirmation
          titre="Supprimer cet Appel d'Offres ?"
          message={`"${aoASupprimer.appel_offre.nom}" et tous ses documents seront définitivement supprimés. Cette action est irréversible.`}
          texteConfirmation="Supprimer"
          dangereux
          enCours={suppressionEnCours}
          erreur={erreurSuppression}
          onConfirmer={confirmerSuppression}
          onAnnuler={() => {
            if (suppressionEnCours) return;
            setAoASupprimer(null);
            setErreurSuppression(null);
          }}
        />
      )}
    </Layout>
  );
}
