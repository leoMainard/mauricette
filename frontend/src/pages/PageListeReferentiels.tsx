import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ErreurApi } from "../api/client";
import { creerReferentiel, listerReferentiels } from "../api/referentielApi";
import type { ContenuReferentiel, ReferentielAvecStatistiques } from "../api/types";
import { Interrupteur } from "../components/Interrupteur";
import { Layout } from "../components/Layout";

const CONTENU_VIDE: ContenuReferentiel = { nom: "", description: "", actif_par_defaut: false };

/** Page liste : les référentiels de questions, avec recherche et création inline. */
export function PageListeReferentiels() {
  const navigate = useNavigate();
  const [terme, setTerme] = useState("");
  const [referentiels, setReferentiels] = useState<ReferentielAvecStatistiques[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const [formulaireOuvert, setFormulaireOuvert] = useState(false);
  const [contenu, setContenu] = useState<ContenuReferentiel>(CONTENU_VIDE);
  const [creationEnCours, setCreationEnCours] = useState(false);

  async function recharger() {
    try {
      const resultats = await listerReferentiels(terme);
      setReferentiels(resultats);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement");
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    let annule = false;
    setChargement(true);
    const delai = setTimeout(async () => {
      if (!annule) await recharger();
    }, 300);
    return () => {
      annule = true;
      clearTimeout(delai);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [terme]);

  async function creer(evenement: React.FormEvent) {
    evenement.preventDefault();
    setCreationEnCours(true);
    setErreur(null);
    try {
      const referentiel = await creerReferentiel(contenu);
      navigate(`/referentiels/${referentiel.id}`);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la création du référentiel.");
      setCreationEnCours(false);
    }
  }

  return (
    <Layout
      barreSuperieure={
        <input
          type="search"
          value={terme}
          onChange={(e) => setTerme(e.target.value)}
          placeholder="Rechercher un référentiel..."
          aria-label="Rechercher un référentiel"
          className="champ-recherche"
        />
      }
    >
      <div className="entete-page entete-page--avec-action">
        <div>
          <h1>Mes référentiels</h1>
          <p className="texte-discret">
            {referentiels.length} référentiel{referentiels.length > 1 ? "s" : ""} · organise tes questions
            et applique-les à tes AO.
          </p>
        </div>
        {!formulaireOuvert && (
          <button type="button" onClick={() => setFormulaireOuvert(true)}>
            + Ajouter un référentiel
          </button>
        )}
      </div>

      {formulaireOuvert && (
        <form onSubmit={creer} className="carte carte--formulaire-inline">
          <h2>Nouveau référentiel</h2>

          <label htmlFor="nom-referentiel">Nom</label>
          <input
            id="nom-referentiel"
            type="text"
            value={contenu.nom}
            onChange={(e) => setContenu((p) => ({ ...p, nom: e.target.value }))}
            placeholder="ex : Modèle de questions standard"
            required
            disabled={creationEnCours}
            autoFocus
          />

          <label htmlFor="description-referentiel">Description</label>
          <input
            id="description-referentiel"
            type="text"
            value={contenu.description ?? ""}
            onChange={(e) => setContenu((p) => ({ ...p, description: e.target.value }))}
            placeholder="ex : Questions posées automatiquement à chaque AO déposé."
            disabled={creationEnCours}
          />

          <div className="ligne-interrupteur">
            <Interrupteur
              coche={contenu.actif_par_defaut}
              onChange={(valeur) => setContenu((p) => ({ ...p, actif_par_defaut: valeur }))}
              disabled={creationEnCours}
              libelle="Appliquer par défaut à chaque nouvel AO"
            />
            <span>Appliquer par défaut à chaque nouvel AO</span>
          </div>

          {erreur && <p className="message-erreur">{erreur}</p>}

          <div style={{ display: "flex", gap: "8px" }}>
            <button type="submit" disabled={creationEnCours || !contenu.nom.trim()}>
              {creationEnCours ? "Création..." : "✓ Enregistrer"}
            </button>
            <button
              type="button"
              className="bouton-fantome"
              onClick={() => {
                setFormulaireOuvert(false);
                setContenu(CONTENU_VIDE);
                setErreur(null);
              }}
              disabled={creationEnCours}
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {erreur && !formulaireOuvert && <p className="message-erreur">{erreur}</p>}

      {chargement ? (
        <p className="texte-discret">Chargement...</p>
      ) : referentiels.length === 0 ? (
        <p className="texte-discret">
          {terme ? "Aucun référentiel ne correspond à cette recherche." : "Aucun référentiel pour le moment."}
        </p>
      ) : (
        <div className="carte carte--tableau">
          <div className="tableau-defilant">
            <table className="table-documents">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Sections</th>
                  <th>Questions actives</th>
                  <th>AO concernés</th>
                  <th>Par défaut</th>
                </tr>
              </thead>
              <tbody>
                {referentiels.map(({ referentiel, nombre_sections, nombre_questions_actives, nombre_ao_concernes }) => (
                  <tr
                    key={referentiel.id}
                    className="ligne-cliquable"
                    tabIndex={0}
                    onClick={() => navigate(`/referentiels/${referentiel.id}`)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") navigate(`/referentiels/${referentiel.id}`);
                    }}
                  >
                    <td className="cellule-nom-ao">
                      {referentiel.nom}
                      {referentiel.description && (
                        <div className="texte-discret">{referentiel.description}</div>
                      )}
                    </td>
                    <td>{nombre_sections}</td>
                    <td>{nombre_questions_actives}</td>
                    <td>{nombre_ao_concernes}</td>
                    <td>
                      {referentiel.actif_par_defaut ? (
                        <span className="badge badge--actif">
                          <span className="badge__point" aria-hidden="true" />
                          Oui
                        </span>
                      ) : (
                        <span className="badge badge--archive">Non</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Layout>
  );
}
