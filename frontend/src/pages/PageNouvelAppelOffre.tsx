import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { creerAppelOffre, deposerDocument } from "../api/appelsOffreApi";
import { ErreurApi } from "../api/client";
import type { DocumentDepose } from "../api/types";
import { ArborescenceDocuments } from "../components/ArborescenceDocuments";
import { ListeFichiersEnAttente } from "../components/ListeFichiersEnAttente";
import { SuiviDepot, type SuiviFichier } from "../components/SuiviDepot";
import { ZoneDepotFichiers } from "../components/ZoneDepotFichiers";

/** Page de création d'un nouvel Appel d'Offres : nom + dépôt de fichiers en un seul geste. */
export function PageNouvelAppelOffre() {
  const navigate = useNavigate();

  const [nom, setNom] = useState("");
  const [fichiersEnAttente, setFichiersEnAttente] = useState<File[]>([]);
  const [enCours, setEnCours] = useState(false);
  const [erreurGlobale, setErreurGlobale] = useState<string | null>(null);

  const [appelOffreCreeId, setAppelOffreCreeId] = useState<string | null>(null);
  const [suivis, setSuivis] = useState<SuiviFichier[]>([]);
  const [documentsCrees, setDocumentsCrees] = useState<DocumentDepose[]>([]);

  function ajouterFichiers(nouveaux: File[]) {
    setFichiersEnAttente((precedent) => [...precedent, ...nouveaux]);
  }

  function retirerFichier(index: number) {
    setFichiersEnAttente((precedent) => precedent.filter((_, i) => i !== index));
  }

  async function creerEtDeposerTout(evenement: React.FormEvent) {
    evenement.preventDefault();
    setErreurGlobale(null);
    setEnCours(true);

    let appelOffreId: string;
    try {
      const appelOffre = await creerAppelOffre(nom);
      appelOffreId = appelOffre.id;
    } catch (e) {
      setErreurGlobale(e instanceof ErreurApi ? e.message : "Erreur lors de la création de l'Appel d'Offres.");
      setEnCours(false);
      return;
    }
    setAppelOffreCreeId(appelOffreId);
    setSuivis(fichiersEnAttente.map((fichier) => ({ nomFichier: fichier.name, statut: "en_cours" })));

    await Promise.all(
      fichiersEnAttente.map(async (fichier, index) => {
        try {
          const resultat = await deposerDocument(appelOffreId, fichier);
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
        {!appelOffreCreeId ? (
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
            <div className="carte">
              <h2>Envoi des documents</h2>
              <SuiviDepot suivis={suivis} />
            </div>
            <div className="carte">
              <h2>Arborescence déposée</h2>
              <ArborescenceDocuments documents={documentsCrees} />
            </div>
            <button
              type="button"
              disabled={enCours}
              onClick={() => navigate(`/appels-offre/${appelOffreCreeId}`)}
            >
              {enCours ? "Envoi en cours..." : "Voir l'Appel d'Offres"}
            </button>
          </>
        )}
      </main>
    </div>
  );
}
