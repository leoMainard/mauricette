import { Route, Routes } from "react-router-dom";
import "./App.css";
import { PageDetailAppelOffre } from "./pages/PageDetailAppelOffre";
import { PageListeAppelsOffre } from "./pages/PageListeAppelsOffre";
import { PageNouvelAppelOffre } from "./pages/PageNouvelAppelOffre";

function App() {
  return (
    <Routes>
      <Route path="/" element={<PageListeAppelsOffre />} />
      <Route path="/appels-offre/nouveau" element={<PageNouvelAppelOffre />} />
      <Route path="/appels-offre/:id" element={<PageDetailAppelOffre />} />
    </Routes>
  );
}

export default App;
