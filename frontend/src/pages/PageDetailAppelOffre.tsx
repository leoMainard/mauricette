import { Check, Pencil, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  deposerDocument,
  obtenirAppelOffre,
  renommerAppelOffre,
  supprimerDocument,
} from "../api/appelsOffreApi";
import { ErreurApi } from "../api/client";
import {
  attacherReferentiel,
  detacherReferentiel,
  listerReferentiels,
  listerReferentielsDeAppelOffre,
} from "../api/referentielApi";
import type { AppelOffre, DocumentDepose, Referentiel, StatutAppelOffre } from "../api/types";
import { ArborescenceDocuments } from "../components/ArborescenceDocuments";
import { Badge } from "../components/Badge";
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

  const [referentielsAttaches, setReferentielsAttaches] = useState<Referentiel[]>([]);
  const [referentielsDisponibles, setReferentielsDisponibles] = useState<Referentiel[]>([]);
  const [referentielChoisi, setReferentielChoisi] = useState("");
  const [referentielActionEnCours, setReferentielActionEnCours] = useState(false);

  async function chargerReferentiels() {
    if (!id) return;
    const [attaches, tous] = await Promise.all([
      listerReferentielsDeAppelOffre(id),
      listerReferentiels(),
    ]);
    setReferentielsAttaches(attaches);
    const idsAttaches = new Set(attaches.map((r) => r.id));
    setReferentielsDisponibles(tous.map((r) => r.referentiel).filter((r) => !idsAttaches.has(r.id)));
  }

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

    chargerReferentiels().catch((e) => {
      if (!annule) setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement des référentiels");
    });

    return () => {
      annule = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function attacher() {
    if (!id || !referentielChoisi) return;
    setReferentielActionEnCours(true);
    try {
      await attacherReferentiel(id, referentielChoisi);
      setReferentielChoisi("");
      await chargerReferentiels();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors du rattachement.");
    } finally {
      setReferentielActionEnCours(false);
    }
  }

  async function detacher(referentielId: string) {
    if (!id) return;
    setReferentielActionEnCours(true);
    try {
      await detacherReferentiel(id, referentielId);
      await chargerReferentiels();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors du détachement.");
    } finally {
      setReferentielActionEnCours(false);
    }
  }

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
      {erreur && <p className="message-erreur">{erreur}</p>}

      <div className="disposition-detail">
        <div className="colonne-detail">
        <div className="carte carte--infos-ao">
          {enEditionNom ? (
            <div className="edition-nom">
              <input
                type="text"
                value={nomEnCours}
                onChange={(e) => setNomEnCours(e.target.value)}
                disabled={renommageEnCours}
                autoFocus
              />
              <button
                type="button"
                className="bouton-icone bouton-icone--valider"
                onClick={enregistrerNom}
                disabled={renommageEnCours || !nomEnCours.trim()}
                title="Enregistrer"
                aria-label="Enregistrer le nouveau nom"
              >
                <Check size={17} />
              </button>
              <button
                type="button"
                className="bouton-icone bouton-icone--annuler"
                onClick={() => {
                  setEnEditionNom(false);
                  setNomEnCours(appelOffre.nom);
                }}
                disabled={renommageEnCours}
                title="Annuler"
                aria-label="Annuler le renommage"
              >
                <X size={17} />
              </button>
            </div>
          ) : (
            <div className="carte--resume">
              <h2>{appelOffre.nom}</h2>
              <button
                type="button"
                className="bouton-icone"
                onClick={() => setEnEditionNom(true)}
                title="Renommer"
                aria-label="Renommer l'Appel d'Offres"
              >
                <Pencil size={16} />
              </button>
            </div>
          )}

          <dl className="grille-infos">
            <div className="grille-infos__item">
              <dt>Statut</dt>
              <dd>
                <Badge statut={appelOffre.statut} libelle={LIBELLES_STATUT[appelOffre.statut]} />
              </dd>
            </div>
            <div className="grille-infos__item">
              <dt>Créé par</dt>
              <dd>{appelOffre.cree_par}</dd>
            </div>
            <div className="grille-infos__item">
              <dt>Créé le</dt>
              <dd>{formaterDateHeure(appelOffre.date_creation)}</dd>
            </div>
            <div className="grille-infos__item">
              <dt>Dernière modification</dt>
              <dd>{formaterDateHeure(appelOffre.date_maj)}</dd>
            </div>
            <div className="grille-infos__item">
              <dt>Documents</dt>
              <dd>
                {documents.length} · {formaterTaille(tailleTotale)}
              </dd>
            </div>
          </dl>
        </div>

        <div className="carte">
          <h2>Référentiels appliqués</h2>
          {referentielsAttaches.length === 0 ? (
            <p className="texte-discret">Aucun référentiel appliqué à cet AO.</p>
          ) : (
            <ul className="liste-referentiels-ao">
              {referentielsAttaches.map((referentiel) => (
                <li key={referentiel.id}>
                  <Link to={`/referentiels/${referentiel.id}`}>{referentiel.nom}</Link>
                  <button
                    type="button"
                    className="bouton-icone bouton-icone--annuler"
                    onClick={() => detacher(referentiel.id)}
                    disabled={referentielActionEnCours}
                    title="Retirer ce référentiel"
                    aria-label={`Retirer ${referentiel.nom}`}
                  >
                    <Trash2 size={14} />
                  </button>
                </li>
              ))}
            </ul>
          )}
          {referentielsDisponibles.length > 0 && (
            <div className="ligne-ajout-referentiel">
              <select
                value={referentielChoisi}
                onChange={(e) => setReferentielChoisi(e.target.value)}
                disabled={referentielActionEnCours}
              >
                <option value="">Choisir un référentiel à ajouter...</option>
                {referentielsDisponibles.map((referentiel) => (
                  <option key={referentiel.id} value={referentiel.id}>
                    {referentiel.nom}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={attacher}
                disabled={referentielActionEnCours || !referentielChoisi}
              >
                Ajouter
              </button>
            </div>
          )}
        </div>
        </div>

        <div className="carte carte--documents">
          <h2>Documents</h2>
          <ZoneDepotFichiers onFichiersAjoutes={ajouterFichiers} />
          <SuiviDepot suivis={suivis} />
          <ArborescenceDocuments
            documents={documents}
            onSupprimer={supprimer}
            suppressionEnCours={suppressionEnCours}
          />
        </div>
      </div>
    </Layout>
  );
}
