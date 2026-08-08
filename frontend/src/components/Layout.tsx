import { BookOpen, FolderOpen, LayoutDashboard, LogOut, Plus, User, Users } from "lucide-react";
import type { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
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
  const navigate = useNavigate();
  const { utilisateur, deconnecter } = useAuth();

  async function seDeconnecter() {
    await deconnecter();
    navigate("/connexion");
  }

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

        {utilisateur && (
          <div className="barre-laterale__pied">
            <Link to="/profil" className="barre-laterale__utilisateur">
              <User size={18} />
              <div className="barre-laterale__utilisateur-info">
                <span className="barre-laterale__utilisateur-nom">{utilisateur.nom}</span>
                <span className="barre-laterale__utilisateur-email">{utilisateur.email}</span>
              </div>
            </Link>
            {utilisateur.statut === "admin" && (
              <>
                <Link
                  to="/admin/tableau-de-bord"
                  className={`barre-laterale__lien${emplacement.pathname.startsWith("/admin/tableau-de-bord") ? " barre-laterale__lien--actif" : ""}`}
                >
                  <LayoutDashboard size={18} />
                  Tableau de bord
                </Link>
                <Link
                  to="/admin/groupes"
                  className={`barre-laterale__lien${emplacement.pathname.startsWith("/admin/groupes") ? " barre-laterale__lien--actif" : ""}`}
                >
                  <Users size={18} />
                  Groupes
                </Link>
              </>
            )}
            <button type="button" className="barre-laterale__deconnexion" onClick={seDeconnecter}>
              <LogOut size={18} />
              Déconnexion
            </button>
          </div>
        )}
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
