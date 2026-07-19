import { useState } from "react";
import "./App.css";
import { creerAppelOffre, deposerDocument } from "./api/appelsOffreApi";
import { ErreurApi } from "./api/client";
import type { AppelOffre, DocumentDepose } from "./api/types";
import { ListeDocuments } from "./components/ListeDocuments";
import { ListeFichiersEnAttente } from "./components/ListeFichiersEnAttente";
import { SuiviDepot, type SuiviFichier } from "./components/SuiviDepot";
import { ZoneDepotFichiers } from "./components/ZoneDepotFichiers";

function App() {
  const [nom, setNom] = useState("");
  const [fichiersEnAttente, setFichiersEnAttente] = useState<File[]>([]);
  const [enCours, setEnCours] = useState(false);
  const [erreurGlobale, setErreurGlobale] = useState<string | null>(null);

  const [appelOffreCree, setAppelOffreCree] = useState<AppelOffre | null>(null);
  const [suivis, setSuivis] = useState<SuiviFichier[]>([]);
  const [documentsCrees, setDocumentsCrees] = useState<DocumentDepose[]>([]);

  function ajouterFichiers(nouveaux: File[]) {
    setFichiersEnAttente((precedent) => [...precedent, ...nouveaux]);
  }

  function retirerFichier(index: number) {
    setFichiersEnAttente((precedent) => precedent.filter((_, i) => i !== index));
  }

  function demarrerNouvelAppelOffre() {
    setNom("");
    setFichiersEnAttente([]);
    setAppelOffreCree(null);
    setSuivis([]);
    setDocumentsCrees([]);
    setErreurGlobale(null);
  }

  async function creerEtDeposerTout(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreurGlobale(null);
    setEnCours(true);

    let appelOffre: AppelOffre;
    try {
      appelOffre = await creerAppelOffre(nom);
    } catch (e) {
      setErreurGlobale(e instanceof ErreurApi ? e.message : "Erreur lors de la création de l'Appel d'Offres.");
      setEnCours(false);
      return;
    }
    setAppelOffreCree(appelOffre);
    setSuivis(fichiersEnAttente.map((fichier) => ({ nomFichier: fichier.name, statut: "en_cours" })));

    await Promise.all(
      fichiersEnAttente.map(async (fichier, index) => {
        try {
          const resultat = await deposerDocument(appelOffre.id, fichier);
          setDocumentsCrees((precedent) => [...precedent, ...resultat.documents_crees]);
          const statut: SuiviFichier["statut"] =
            resultat.documents_crees.length > 0 ? "succes" : "doublon";
          setSuivis((precedent) =>
            precedent.map((s, i) => (i === index ? { ...s, statut } : s)),
          );
        } catch (e) {
          const message = e instanceof ErreurApi ? e.message : "Échec du dépôt";
          setSuivis((precedent) =>
            precedent.map((s, i) => (i === index ? { ...s, statut: "erreur", message } : s)),
          );
        }
      }),
    );

    setEnCours(false);
  }

  return (
    <div className="page">
      <header className="entete">
        <h1>Mauricette</h1>
        <p className="texte-discret">
          Dépose ton Appel d'Offres, et laisse Mauricette t'aider à y voir clair.
        </p>
      </header>

      <main className="contenu">
        {!appelOffreCree ? (
          <form onSubmit={creerEtDeposerTout} className="carte">
            <h2>Nouvel Appel d'Offres</h2>
            <label htmlFor="nom-ao">Nom de l'Appel d'Offres</label>
            <input
              id="nom-ao"
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              placeholder="ex : Assurance flotte automobile 2026"
              required
              disabled={enCours}
            />

            <ZoneDepotFichiers onFichiersAjoutes={ajouterFichiers} />
            <ListeFichiersEnAttente fichiers={fichiersEnAttente} onRetirer={retirerFichier} />

            {erreurGlobale && <p className="message-erreur">{erreurGlobale}</p>}

            <button type="submit" disabled={enCours || !nom.trim()}>
              {enCours ? "Création en cours..." : "Créer l'Appel d'Offres"}
            </button>
          </form>
        ) : (
          <>
            <div className="carte carte--resume">
              <div>
                <h2>{appelOffreCree.nom}</h2>
                <p className="texte-discret">Statut : {appelOffreCree.statut}</p>
              </div>
              <button type="button" onClick={demarrerNouvelAppelOffre} disabled={enCours}>
                Nouvel Appel d'Offres
              </button>
            </div>
            <div className="carte">
              <h2>Envoi des documents</h2>
              <SuiviDepot suivis={suivis} />
            </div>
            <ListeDocuments documents={documentsCrees} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
