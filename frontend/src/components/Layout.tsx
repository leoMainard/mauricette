import { Plus } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { LogoMauricette } from "./icones/LogoMauricette";

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
          <LogoMauricette className="barre-laterale__logo" />
          Mauricette
        </Link>
        <Link to="/appels-offre/nouveau" className="bouton-nouvel-ao">
          <Plus size={18} strokeWidth={2.5} />
          Nouvel AO
        </Link>
      </aside>

      <div className="zone-principale">
        <header className="barre-superieure">{barreSuperieure}</header>
        <main className="contenu-principal">{children}</main>
      </div>
    </div>
  );
}
