import { useState } from "react";
import { changerMotDePasse, modifierProfil } from "../api/authApi";
import { ErreurApi } from "../api/client";
import { Layout } from "../components/Layout";
import { useAuth } from "../contexts/AuthContext";

/** Page de profil : modification du nom/email, et changement de mot de passe. */
export function PageProfil() {
  const { utilisateur, rafraichir } = useAuth();

  const [nom, setNom] = useState(utilisateur?.nom ?? "");
  const [email, setEmail] = useState(utilisateur?.email ?? "");
  const [enregistrementProfilEnCours, setEnregistrementProfilEnCours] = useState(false);
  const [erreurProfil, setErreurProfil] = useState<string | null>(null);
  const [succesProfil, setSuccesProfil] = useState(false);

  const [ancienMotDePasse, setAncienMotDePasse] = useState("");
  const [nouveauMotDePasse, setNouveauMotDePasse] = useState("");
  const [changementMotDePasseEnCours, setChangementMotDePasseEnCours] = useState(false);
  const [erreurMotDePasse, setErreurMotDePasse] = useState<string | null>(null);
  const [succesMotDePasse, setSuccesMotDePasse] = useState(false);

  if (!utilisateur) {
    return (
      <Layout>
        <p className="texte-discret">Chargement...</p>
      </Layout>
    );
  }

  async function enregistrerProfil(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreurProfil(null);
    setSuccesProfil(false);
    setEnregistrementProfilEnCours(true);
    try {
      await modifierProfil(nom, email);
      await rafraichir();
      setSuccesProfil(true);
    } catch (e) {
      setErreurProfil(e instanceof ErreurApi ? e.message : "Erreur lors de l'enregistrement.");
    } finally {
      setEnregistrementProfilEnCours(false);
    }
  }

  async function enregistrerMotDePasse(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreurMotDePasse(null);
    setSuccesMotDePasse(false);
    setChangementMotDePasseEnCours(true);
    try {
      await changerMotDePasse(ancienMotDePasse, nouveauMotDePasse);
      setAncienMotDePasse("");
      setNouveauMotDePasse("");
      setSuccesMotDePasse(true);
    } catch (e) {
      setErreurMotDePasse(e instanceof ErreurApi ? e.message : "Erreur lors du changement de mot de passe.");
    } finally {
      setChangementMotDePasseEnCours(false);
    }
  }

  return (
    <Layout>
      <h1>Mon profil</h1>

      <form onSubmit={enregistrerProfil} className="carte">
        <h2>Informations</h2>
        {erreurProfil && <p className="message-erreur">{erreurProfil}</p>}
        {succesProfil && <p className="texte-discret">Profil mis à jour.</p>}

        <label htmlFor="profil-nom">Nom</label>
        <input
          id="profil-nom"
          type="text"
          value={nom}
          onChange={(e) => setNom(e.target.value)}
          required
          disabled={enregistrementProfilEnCours}
        />

        <label htmlFor="profil-email">Email</label>
        <input
          id="profil-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={enregistrementProfilEnCours}
        />

        <button type="submit" disabled={enregistrementProfilEnCours || !nom.trim() || !email.trim()}>
          {enregistrementProfilEnCours ? "Enregistrement..." : "Enregistrer"}
        </button>
      </form>

      <form onSubmit={enregistrerMotDePasse} className="carte">
        <h2>Changer de mot de passe</h2>
        {erreurMotDePasse && <p className="message-erreur">{erreurMotDePasse}</p>}
        {succesMotDePasse && <p className="texte-discret">Mot de passe changé.</p>}

        <label htmlFor="ancien-mot-de-passe">Mot de passe actuel</label>
        <input
          id="ancien-mot-de-passe"
          type="password"
          value={ancienMotDePasse}
          onChange={(e) => setAncienMotDePasse(e.target.value)}
          required
          disabled={changementMotDePasseEnCours}
        />

        <label htmlFor="nouveau-mot-de-passe">Nouveau mot de passe</label>
        <input
          id="nouveau-mot-de-passe"
          type="password"
          value={nouveauMotDePasse}
          onChange={(e) => setNouveauMotDePasse(e.target.value)}
          required
          minLength={8}
          disabled={changementMotDePasseEnCours}
        />

        <button
          type="submit"
          disabled={changementMotDePasseEnCours || !ancienMotDePasse || nouveauMotDePasse.length < 8}
        >
          {changementMotDePasseEnCours ? "Changement..." : "Changer le mot de passe"}
        </button>
      </form>
    </Layout>
  );
}
