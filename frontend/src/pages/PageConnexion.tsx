import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { connecter } from "../api/authApi";
import { ErreurApi } from "../api/client";
import { LogoMauricette } from "../components/icones/LogoMauricette";
import { useAuth } from "../contexts/AuthContext";

/** Page de connexion : email + mot de passe. */
export function PageConnexion() {
  const navigate = useNavigate();
  const { rafraichir } = useAuth();

  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  async function soumettre(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await connecter(email, motDePasse);
      await rafraichir();
      navigate("/");
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la connexion.");
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
        <h2>Connexion</h2>

        {erreur && <p className="message-erreur">{erreur}</p>}

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
          disabled={enCours}
        />

        <label htmlFor="mot-de-passe">Mot de passe</label>
        <input
          id="mot-de-passe"
          type="password"
          value={motDePasse}
          onChange={(e) => setMotDePasse(e.target.value)}
          required
          disabled={enCours}
        />

        <button type="submit" disabled={enCours || !email.trim() || !motDePasse}>
          {enCours ? "Connexion..." : "Se connecter"}
        </button>

        <p className="texte-discret page-auth__lien-secondaire">
          Pas encore de compte ? <Link to="/inscription">Créer un compte</Link>
        </p>
      </form>
    </div>
  );
}
