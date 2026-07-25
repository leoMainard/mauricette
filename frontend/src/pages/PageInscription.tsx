import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { inscrire } from "../api/authApi";
import { ErreurApi } from "../api/client";
import { LogoMauricette } from "../components/icones/LogoMauricette";
import { useAuth } from "../contexts/AuthContext";

/** Page d'inscription : nom + email + mot de passe. Statut USER par défaut. */
export function PageInscription() {
  const navigate = useNavigate();
  const { rafraichir } = useAuth();

  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  async function soumettre(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await inscrire(email, motDePasse, nom);
      await rafraichir();
      navigate("/");
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de l'inscription.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <div className="page-auth">
      <form onSubmit={soumettre} className="carte page-auth__carte">
        <div className="page-auth__marque">
          <LogoMauricette className="barre-laterale__logo" />
          Mauricette
        </div>
        <h2>Créer un compte</h2>

        {erreur && <p className="message-erreur">{erreur}</p>}

        <label htmlFor="nom">Nom</label>
        <input
          id="nom"
          type="text"
          value={nom}
          onChange={(e) => setNom(e.target.value)}
          required
          autoFocus
          disabled={enCours}
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={enCours}
        />

        <label htmlFor="mot-de-passe">Mot de passe</label>
        <input
          id="mot-de-passe"
          type="password"
          value={motDePasse}
          onChange={(e) => setMotDePasse(e.target.value)}
          required
          minLength={8}
          disabled={enCours}
        />
        <p className="texte-discret">Au moins 8 caractères.</p>

        <button type="submit" disabled={enCours || !nom.trim() || !email.trim() || motDePasse.length < 8}>
          {enCours ? "Création..." : "Créer mon compte"}
        </button>

        <p className="texte-discret page-auth__lien-secondaire">
          Déjà un compte ? <Link to="/connexion">Se connecter</Link>
        </p>
      </form>
    </div>
  );
}
