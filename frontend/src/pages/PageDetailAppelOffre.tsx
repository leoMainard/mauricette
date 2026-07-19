import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  deposerDocument,
  obtenirAppelOffre,
  renommerAppelOffre,
  supprimerDocument,
} from "../api/appelsOffreApi";
import { ErreurApi } from "../api/client";
import type { AppelOffre, DocumentDepose, StatutAppelOffre } from "../api/types";
import { ArborescenceDocuments } from "../components/ArborescenceDocuments";
import { Layout } from "../components/Layout";
import { SuiviDepot, type SuiviFichier } from "../components/SuiviDepot";
import { ZoneDepotFichiers } from "../components/ZoneDepotFichiers";

const LIBELLES_STATUT: Record<StatutAppelOffre, string> = {
  brouillon: "Brouillon",
  en_cours: "En cours",
  traite: "Traité",
  archive: "Archivé",
};

function formaterDateHeure(dateIso: string): string {
  return new Date(dateIso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

/** Page de détail d'un Appel d'Offres : métadonnées, renommage, documents (ajout/suppression). */
export function PageDetailAppelOffre() {
  const { id } = useParams<{ id: string }>();

  const [appelOffre, setAppelOffre] = useState<AppelOffre | null>(null);
  const [documents, setDocuments] = useState<DocumentDepose[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const [enEditionNom, setEnEditionNom] = useState(false);
  const [nomEnCours, setNomEnCours] = useState("");
  const [renommageEnCours, setRenommageEnCours] = useState(false);

  const [suivis, setSuivis] = useState<SuiviFichier[]>([]);
  const [suppressionEnCours, setSuppressionEnCours] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!id) return;
    let annule = false;

    obtenirAppelOffre(id)
      .then((detail) => {
        if (annule) return;
        setAppelOffre(detail.appel_offre);
        setDocuments(detail.documents);
        setNomEnCours(detail.appel_offre.nom);
      })
      .catch((e) => {
        if (!annule) setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement");
      })
      .finally(() => {
        if (!annule) setChargement(false);
      });

    return () => {
      annule = true;
    };
  }, [id]);

  async function enregistrerNom() {
    if (!id || !nomEnCours.trim() || !appelOffre) return;
    setRenommageEnCours(true);
    try {
      const misAJour = await renommerAppelOffre(id, nomEnCours.trim());
      setAppelOffre(misAJour);
      setEnEditionNom(false);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors du renommage.");
    } finally {
      setRenommageEnCours(false);
    }
  }

  async function ajouterFichiers(fichiers: File[]) {
    if (!id) return;
    setSuivis((precedent) => [
      ...precedent,
      ...fichiers.map((fichier) => ({ nomFichier: fichier.name, statut: "en_cours" as const })),
    ]);

    for (const fichier of fichiers) {
      try {
        const resultat = await deposerDocument(id, fichier);
        setDocuments((precedent) => [...precedent, ...resultat.documents_crees]);
        const statut: SuiviFichier["statut"] = resultat.documents_crees.length > 0 ? "succes" : "doublon";
        setSuivis((precedent) =>
          precedent.map((s) => (s.nomFichier === fichier.name && s.statut === "en_cours" ? { ...s, statut } : s)),
        );
      } catch (e) {
        const message = e instanceof ErreurApi ? e.message : "Échec du dépôt";
        setSuivis((precedent) =>
          precedent.map((s) =>
            s.nomFichier === fichier.name && s.statut === "en_cours"
              ? { ...s, statut: "erreur", message }
              : s,
          ),
        );
      }
    }
  }

  async function supprimer(document: DocumentDepose) {
    if (!id) return;
    setSuppressionEnCours((precedent) => new Set(precedent).add(document.id));
    try {
      await supprimerDocument(id, document.id);
      setDocuments((precedent) => precedent.filter((d) => d.id !== document.id));
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la suppression.");
    } finally {
      setSuppressionEnCours((precedent) => {
        const suivant = new Set(precedent);
        suivant.delete(document.id);
        return suivant;
      });
    }
  }

  if (chargement) {
    return (
      <Layout>
        <p className="texte-discret">Chargement...</p>
      </Layout>
    );
  }

  if (!appelOffre) {
    return (
      <Layout>
        <p className="message-erreur">{erreur ?? "Appel d'Offres introuvable."}</p>
        <Link to="/">Retour à la liste</Link>
      </Layout>
    );
  }

  const tailleTotale = documents.reduce((total, d) => total + d.taille_octets, 0);

  return (
    <Layout
      barreSuperieure={
        <Link to="/" className="lien-retour">
          ← Retour à la liste
        </Link>
      }
    >
      <div className="carte">
        {enEditionNom ? (
          <>
            <input
              type="text"
              value={nomEnCours}
              onChange={(e) => setNomEnCours(e.target.value)}
              disabled={renommageEnCours}
            />
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                onClick={enregistrerNom}
                disabled={renommageEnCours || !nomEnCours.trim()}
              >
                Enregistrer
              </button>
              <button
                type="button"
                className="bouton-fantome"
                onClick={() => {
                  setEnEditionNom(false);
                  setNomEnCours(appelOffre.nom);
                }}
                disabled={renommageEnCours}
              >
                Annuler
              </button>
            </div>
          </>
        ) : (
          <div className="carte--resume">
            <h2>{appelOffre.nom}</h2>
            <button type="button" className="bouton-fantome" onClick={() => setEnEditionNom(true)}>
              Renommer
            </button>
          </div>
        )}

        <table className="table-documents">
          <tbody>
            <tr>
              <th>Statut</th>
              <td>
                <span className={`badge badge--${appelOffre.statut}`}>
                  {LIBELLES_STATUT[appelOffre.statut]}
                </span>
              </td>
            </tr>
            <tr>
              <th>Créé par</th>
              <td>{appelOffre.cree_par}</td>
            </tr>
            <tr>
              <th>Créé le</th>
              <td>{formaterDateHeure(appelOffre.date_creation)}</td>
            </tr>
            <tr>
              <th>Dernière modification</th>
              <td>{formaterDateHeure(appelOffre.date_maj)}</td>
            </tr>
            <tr>
              <th>Documents</th>
              <td>
                {documents.length} ({formaterTaille(tailleTotale)})
              </td>
            </tr>
          </tbody>
        </table>

        {erreur && <p className="message-erreur">{erreur}</p>}
      </div>

      <div className="carte">
        <h2>Ajouter des documents</h2>
        <ZoneDepotFichiers onFichiersAjoutes={ajouterFichiers} />
        <SuiviDepot suivis={suivis} />
      </div>

      <div className="carte">
        <h2>Documents</h2>
        <ArborescenceDocuments
          documents={documents}
          onSupprimer={supprimer}
          suppressionEnCours={suppressionEnCours}
        />
      </div>
    </Layout>
  );
}
