import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { useAuth } from "./contexts/AuthContext";
import { PageConnexion } from "./pages/PageConnexion";
import { PageDetailAppelOffre } from "./pages/PageDetailAppelOffre";
import { PageDetailReferentiel } from "./pages/PageDetailReferentiel";
import { PageGroupesUtilisateurs } from "./pages/PageGroupesUtilisateurs";
import { PageInscription } from "./pages/PageInscription";
import { PageListeAppelsOffre } from "./pages/PageListeAppelsOffre";
import { PageListeReferentiels } from "./pages/PageListeReferentiels";
import { PageNouvelAppelOffre } from "./pages/PageNouvelAppelOffre";
import { PageProfil } from "./pages/PageProfil";
import { PageTableauDeBordAdmin } from "./pages/PageTableauDeBordAdmin";

function App() {
  const { utilisateur, chargement } = useAuth();

  if (chargement) {
    return <p className="texte-discret">Chargement...</p>;
  }

  if (!utilisateur) {
    return (
      <Routes>
        <Route path="/connexion" element={<PageConnexion />} />
        <Route path="/inscription" element={<PageInscription />} />
        <Route path="*" element={<Navigate to="/connexion" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<PageListeAppelsOffre />} />
      <Route path="/appels-offre/nouveau" element={<PageNouvelAppelOffre />} />
      <Route path="/appels-offre/:id" element={<PageDetailAppelOffre />} />
      <Route path="/referentiels" element={<PageListeReferentiels />} />
      <Route path="/referentiels/:id" element={<PageDetailReferentiel />} />
      <Route path="/profil" element={<PageProfil />} />
      {utilisateur.statut === "admin" && (
        <>
          <Route path="/admin/tableau-de-bord" element={<PageTableauDeBordAdmin />} />
          <Route path="/admin/groupes" element={<PageGroupesUtilisateurs />} />
        </>
      )}
      <Route path="/connexion" element={<Navigate to="/" replace />} />
      <Route path="/inscription" element={<Navigate to="/" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
