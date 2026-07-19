import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface Props {
  children: ReactNode;
  /** Contenu affiché dans la barre supérieure (ex: recherche, fil d'ariane). */
  barreSuperieure?: ReactNode;
}

/**
 * Ossature de l'application : sidebar fixe à gauche (marque + actions
 * globales) et zone principale (barre supérieure + contenu de la page).
 * D'autres éléments de navigation viendront s'ajouter à la sidebar plus tard.
 */
export function Layout({ children, barreSuperieure }: Props) {
  return (
    <div className="app-shell">
      <aside className="barre-laterale">
        <Link to="/" className="barre-laterale__marque">
          Mauricette
        </Link>
        <Link to="/appels-offre/nouveau" className="bouton-nouvel-ao">
          + Nouvel AO
        </Link>
      </aside>

      <div className="zone-principale">
        <header className="barre-superieure">{barreSuperieure}</header>
        <main className="contenu-principal">{children}</main>
      </div>
    </div>
  );
}
