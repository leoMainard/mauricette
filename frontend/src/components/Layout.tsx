import { BookOpen, FolderOpen, Plus } from "lucide-react";
import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { LogoMauricette } from "./icones/LogoMauricette";

interface Props {
  children: ReactNode;
  /** Contenu affiché dans la barre supérieure (ex: recherche, fil d'ariane). */
  barreSuperieure?: ReactNode;
  /** Désactive la largeur maximale du contenu (ex: pages avec disposition en colonnes). */
  pleineLargeur?: boolean;
}

const LIENS_NAVIGATION = [
  { chemin: "/", label: "Mes Appels d'Offres", Icone: FolderOpen },
  { chemin: "/referentiels", label: "Référentiels", Icone: BookOpen },
];

/**
 * Ossature de l'application : sidebar fixe à gauche (marque, action globale et
 * navigation) et zone principale (barre supérieure + contenu de la page).
 */
export function Layout({ children, barreSuperieure, pleineLargeur }: Props) {
  const emplacement = useLocation();

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

        <nav className="barre-laterale__navigation">
          {LIENS_NAVIGATION.map(({ chemin, label, Icone }) => {
            const estActif = chemin === "/" ? emplacement.pathname === "/" : emplacement.pathname.startsWith(chemin);
            return (
              <Link
                key={chemin}
                to={chemin}
                className={`barre-laterale__lien${estActif ? " barre-laterale__lien--actif" : ""}`}
              >
                <Icone size={18} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="zone-principale">
        <header className="barre-superieure">{barreSuperieure}</header>
        <main className={`contenu-principal${pleineLargeur ? " contenu-principal--pleine-largeur" : ""}`}>
          {children}
        </main>
      </div>
    </div>
  );
}
