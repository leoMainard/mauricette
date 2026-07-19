import { Link } from "react-router-dom";

/** Bandeau d'application partagé par toutes les pages : marque + slogan. */
export function EnTeteApplication() {
  return (
    <header className="entete-app">
      <div className="entete-app__contenu">
        <Link to="/" className="entete-app__marque">
          Mauricette
        </Link>
        <p className="entete-app__slogan">
          Dépose ton Appel d'Offres, et laisse Mauricette t'aider à y voir clair.
        </p>
      </div>
    </header>
  );
}
