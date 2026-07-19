import { Route, Routes } from "react-router-dom";
import "./App.css";
import { PageDetailAppelOffre } from "./pages/PageDetailAppelOffre";
import { PageDetailReferentiel } from "./pages/PageDetailReferentiel";
import { PageListeAppelsOffre } from "./pages/PageListeAppelsOffre";
import { PageListeReferentiels } from "./pages/PageListeReferentiels";
import { PageNouvelAppelOffre } from "./pages/PageNouvelAppelOffre";

function App() {
  return (
    <Routes>
      <Route path="/" element={<PageListeAppelsOffre />} />
      <Route path="/appels-offre/nouveau" element={<PageNouvelAppelOffre />} />
      <Route path="/appels-offre/:id" element={<PageDetailAppelOffre />} />
      <Route path="/referentiels" element={<PageListeReferentiels />} />
      <Route path="/referentiels/:id" element={<PageDetailReferentiel />} />
    </Routes>
  );
}

export default App;
