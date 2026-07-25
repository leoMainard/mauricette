import { useEffect, useState } from "react";
import { ErreurApi } from "../api/client";
import type { GroupeUtilisateur, Utilisateur } from "../api/types";
import { affecterGroupe, creerGroupe, listerGroupes, listerUtilisateurs } from "../api/utilisateurApi";
import { Layout } from "../components/Layout";

/** Page d'administration : création de groupes d'utilisateurs et affectation des membres. */
export function PageGroupesUtilisateurs() {
  const [groupes, setGroupes] = useState<GroupeUtilisateur[]>([]);
  const [utilisateurs, setUtilisateurs] = useState<Utilisateur[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const [nomNouveauGroupe, setNomNouveauGroupe] = useState("");
  const [creationEnCours, setCreationEnCours] = useState(false);
  const [affectationEnCoursId, setAffectationEnCoursId] = useState<string | null>(null);

  async function recharger() {
    try {
      const [groupesCharges, utilisateursCharges] = await Promise.all([
        listerGroupes(),
        listerUtilisateurs(),
      ]);
      setGroupes(groupesCharges);
      setUtilisateurs(utilisateursCharges);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement.");
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    recharger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function creerNouveauGroupe(evenement: React.FormEvent) {
    evenement.preventDefault();
    if (!nomNouveauGroupe.trim()) return;
    setCreationEnCours(true);
    try {
      await creerGroupe(nomNouveauGroupe.trim());
      setNomNouveauGroupe("");
      await recharger();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la création du groupe.");
    } finally {
      setCreationEnCours(false);
    }
  }

  async function changerGroupe(utilisateurId: string, groupeId: string) {
    setAffectationEnCoursId(utilisateurId);
    try {
      await affecterGroupe(utilisateurId, groupeId || null);
      await recharger();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de l'affectation.");
    } finally {
      setAffectationEnCoursId(null);
    }
  }

  if (chargement) {
    return (
      <Layout>
        <p className="texte-discret">Chargement...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1>Groupes d'utilisateurs</h1>
      {erreur && <p className="message-erreur">{erreur}</p>}

      <form onSubmit={creerNouveauGroupe} className="carte carte--formulaire-inline">
        <label htmlFor="nom-groupe">Nouveau groupe</label>
        <input
          id="nom-groupe"
          type="text"
          value={nomNouveauGroupe}
          onChange={(e) => setNomNouveauGroupe(e.target.value)}
          placeholder="ex : Équipe Assurance Dommages"
          required
          disabled={creationEnCours}
        />
        <button type="submit" disabled={creationEnCours || !nomNouveauGroupe.trim()}>
          Créer
        </button>
      </form>

      <div className="carte">
        <h2>Utilisateurs {utilisateurs.length}</h2>
        {utilisateurs.length === 0 ? (
          <p className="texte-discret">Aucun utilisateur pour le moment.</p>
        ) : (
          <table className="table-documents">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Statut</th>
                <th>Groupe</th>
              </tr>
            </thead>
            <tbody>
              {utilisateurs.map((utilisateur) => (
                <tr key={utilisateur.id}>
                  <td>{utilisateur.nom}</td>
                  <td>{utilisateur.email}</td>
                  <td>{utilisateur.statut === "admin" ? "Admin" : "Utilisateur"}</td>
                  <td>
                    <select
                      value={utilisateur.groupe_id ?? ""}
                      onChange={(e) => changerGroupe(utilisateur.id, e.target.value)}
                      disabled={affectationEnCoursId === utilisateur.id}
                    >
                      <option value="">Aucun groupe</option>
                      {groupes.map((groupe) => (
                        <option key={groupe.id} value={groupe.id}>
                          {groupe.nom}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Layout>
  );
}
