import { Check, FolderOpen, ListChecks, Pencil, X } from "lucide-react";
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
  obtenirReferentiel,
} from "../api/referentielApi";
import {
  listerReponsesAppelOffre,
  obtenirTraitementAppelOffre,
  reanalyserAppelOffre,
  relancerDocument,
  validerReponse,
} from "../api/traitementRagApi";
import type {
  AppelOffre,
  DetailReferentiel,
  DocumentDepose,
  DocumentTraitementRag,
  Referentiel,
  ReponseQuestion,
  StatutAppelOffre,
} from "../api/types";
import { Badge } from "../components/Badge";
import { Layout } from "../components/Layout";
import { OngletDocuments } from "../components/OngletDocuments";
import { OngletQuestions } from "../components/OngletQuestions";
import type { SuiviFichier } from "../components/SuiviDepot";

// Intervalle de sondage de l'état du pipeline RAG, tant qu'au moins un document
// n'est pas encore dans un état final (reussi/echec).
const INTERVALLE_SONDAGE_TRAITEMENT_MS = 4000;

const LIBELLES_STATUT: Record<StatutAppelOffre, string> = {
  brouillon: "Brouillon",
  en_cours: "En cours",
  traite: "Traité",
  archive: "Archivé",
};

type Onglet = "documents" | "questions";

function formaterDateHeure(dateIso: string): string {
  return new Date(dateIso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Page de détail d'un Appel d'Offres : en-tête + onglets Documents / Questions. */
export function PageDetailAppelOffre() {
  const { id } = useParams<{ id: string }>();

  const [appelOffre, setAppelOffre] = useState<AppelOffre | null>(null);
  const [documents, setDocuments] = useState<DocumentDepose[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const [ongletActif, setOngletActif] = useState<Onglet>("documents");

  const [enEditionNom, setEnEditionNom] = useState(false);
  const [nomEnCours, setNomEnCours] = useState("");
  const [renommageEnCours, setRenommageEnCours] = useState(false);

  const [suivis, setSuivis] = useState<SuiviFichier[]>([]);
  const [suppressionEnCours, setSuppressionEnCours] = useState<Set<string>>(new Set());

  const [traitements, setTraitements] = useState<Map<string, DocumentTraitementRag>>(new Map());
  const [relanceEnCours, setRelanceEnCours] = useState<Set<string>>(new Set());
  // Incrémenté après tout événement pouvant relancer le pipeline RAG (dépôt, relance,
  // suppression), pour redémarrer le sondage même s'il s'était arrêté (tout était traité).
  const [versionTraitement, setVersionTraitement] = useState(0);

  const [referentielsAttaches, setReferentielsAttaches] = useState<Referentiel[]>([]);
  const [referentielsDisponibles, setReferentielsDisponibles] = useState<Referentiel[]>([]);
  const [referentielChoisi, setReferentielChoisi] = useState("");
  const [referentielActionEnCours, setReferentielActionEnCours] = useState(false);

  const [detailsReferentiels, setDetailsReferentiels] = useState<DetailReferentiel[]>([]);
  const [reponsesParQuestion, setReponsesParQuestion] = useState<Map<string, ReponseQuestion>>(
    new Map(),
  );
  const [chargementQuestions, setChargementQuestions] = useState(true);
  const [validationEnCoursId, setValidationEnCoursId] = useState<string | null>(null);
  const [declenchementReanalyseEnCours, setDeclenchementReanalyseEnCours] = useState(false);

  async function chargerQuestions(referentiels: Referentiel[]) {
    if (!id) return;
    setChargementQuestions(true);
    try {
      const [details, reponses] = await Promise.all([
        Promise.all(referentiels.map((r) => obtenirReferentiel(r.id))),
        listerReponsesAppelOffre(id),
      ]);
      setDetailsReferentiels(details);
      setReponsesParQuestion(new Map(reponses.map((r) => [r.question_referentiel_id, r])));
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement des questions.");
    } finally {
      setChargementQuestions(false);
    }
  }

  async function chargerReferentiels() {
    if (!id) return;
    const [attaches, tous] = await Promise.all([
      listerReferentielsDeAppelOffre(id),
      listerReferentiels(),
    ]);
    setReferentielsAttaches(attaches);
    const idsAttaches = new Set(attaches.map((r) => r.id));
    setReferentielsDisponibles(tous.map((r) => r.referentiel).filter((r) => !idsAttaches.has(r.id)));
    await chargerQuestions(attaches);
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

  useEffect(() => {
    if (!id) return;
    let annule = false;
    let minuteur: ReturnType<typeof setTimeout> | undefined;

    async function sonder() {
      try {
        const resultats = await obtenirTraitementAppelOffre(id!);
        if (annule) return;
        setTraitements(new Map(resultats.map((t) => [t.document_id, t])));
        const enCours = resultats.some(
          (t) => t.statut_global === "en_attente" || t.statut_global === "en_cours",
        );
        if (enCours) {
          minuteur = setTimeout(sonder, INTERVALLE_SONDAGE_TRAITEMENT_MS);
        }
      } catch {
        // Le suivi du traitement est une amélioration d'affichage : une erreur ici
        // ne doit pas bloquer le reste de la page ni afficher un message d'erreur.
      }
    }

    sonder();

    return () => {
      annule = true;
      if (minuteur) clearTimeout(minuteur);
    };
  }, [id, versionTraitement]);

  // Rafraîchit les réponses à chaque retour sur l'onglet Questions (la régénération
  // se fait en tâche de fond côté serveur, sans notification push vers le client).
  useEffect(() => {
    if (ongletActif === "questions") {
      chargerQuestions(referentielsAttaches).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ongletActif]);

  // Tant que l'AO est "en cours" (analyse en cours, ex: après une ré-analyse
  // manuelle), sonde périodiquement son statut et rafraîchit les réponses dès
  // que l'analyse se termine. S'arrête naturellement dès que le statut change.
  useEffect(() => {
    if (!id || appelOffre?.statut !== "en_cours") return;
    let annule = false;
    const minuteur = setTimeout(async () => {
      try {
        const detail = await obtenirAppelOffre(id);
        if (annule) return;
        setAppelOffre(detail.appel_offre);
        if (detail.appel_offre.statut !== "en_cours") {
          await chargerQuestions(referentielsAttaches);
        }
      } catch {
        // Amélioration d'affichage : une erreur ici ne doit pas bloquer la page.
      }
    }, INTERVALLE_SONDAGE_TRAITEMENT_MS);

    return () => {
      annule = true;
      clearTimeout(minuteur);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, appelOffre?.statut]);

  async function reanalyser() {
    if (!id) return;
    setDeclenchementReanalyseEnCours(true);
    try {
      await reanalyserAppelOffre(id);
      const detail = await obtenirAppelOffre(id);
      setAppelOffre(detail.appel_offre);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors du déclenchement de la ré-analyse.");
    } finally {
      setDeclenchementReanalyseEnCours(false);
    }
  }

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

  async function valider(reponse: ReponseQuestion) {
    setValidationEnCoursId(reponse.id);
    try {
      const misAJour = await validerReponse(reponse.id);
      setReponsesParQuestion((precedent) => {
        const suivant = new Map(precedent);
        suivant.set(misAJour.question_referentiel_id, misAJour);
        return suivant;
      });
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la validation.");
    } finally {
      setValidationEnCoursId(null);
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
        if (resultat.documents_crees.length > 0) {
          setVersionTraitement((v) => v + 1);
        }
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
      setVersionTraitement((v) => v + 1);
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

  async function relancer(document: DocumentDepose) {
    if (!id) return;
    setRelanceEnCours((precedent) => new Set(precedent).add(document.id));
    try {
      await relancerDocument(id, document.id);
      setVersionTraitement((v) => v + 1);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la relance.");
    } finally {
      setRelanceEnCours((precedent) => {
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

  const questionsActivesTotal = detailsReferentiels.reduce(
    (total, d) => total + d.sections.flatMap((s) => s.questions).filter((q) => q.actif).length,
    0,
  );
  const reponsesGenereesTotal = detailsReferentiels.reduce(
    (total, d) =>
      total +
      d.sections
        .flatMap((s) => s.questions)
        .filter((q) => q.actif && reponsesParQuestion.get(q.id)?.contenu).length,
    0,
  );

  return (
    <Layout
      barreSuperieure={
        <Link to="/" className="lien-retour">
          ← Tous les AO
        </Link>
      }
    >
      {erreur && <p className="message-erreur">{erreur}</p>}

      <div className="entete-fiche-ao">
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
          <div className="entete-fiche-ao__titre">
            <h1>{appelOffre.nom}</h1>
            <Badge statut={appelOffre.statut} libelle={LIBELLES_STATUT[appelOffre.statut]} />
            <button
              type="button"
              className="bouton-icone"
              onClick={() => setEnEditionNom(true)}
              title="Renommer"
              aria-label="Renommer l'Appel d'Offres"
            >
              <Pencil size={15} />
            </button>
          </div>
        )}

        <div className="entete-fiche-ao__meta">
          <span>Créé par {appelOffre.cree_par}</span>
          <span>·</span>
          <span>Créé le {formaterDateHeure(appelOffre.date_creation)}</span>
          <span>·</span>
          <span>Dernière modification {formaterDateHeure(appelOffre.date_maj)}</span>
        </div>
      </div>

      <div className="barre-onglets">
        <button
          type="button"
          className={`onglet${ongletActif === "documents" ? " onglet--actif" : ""}`}
          onClick={() => setOngletActif("documents")}
        >
          <FolderOpen size={16} />
          Documents
          <span className="onglet__compte">{documents.length}</span>
        </button>
        <button
          type="button"
          className={`onglet${ongletActif === "questions" ? " onglet--actif" : ""}`}
          onClick={() => setOngletActif("questions")}
        >
          <ListChecks size={16} />
          Questions
          <span className="onglet__compte">
            {reponsesGenereesTotal}/{questionsActivesTotal}
          </span>
        </button>
      </div>

      {ongletActif === "documents" ? (
        <OngletDocuments
          documents={documents}
          suivis={suivis}
          suppressionEnCours={suppressionEnCours}
          traitements={traitements}
          relanceEnCours={relanceEnCours}
          onAjouterFichiers={ajouterFichiers}
          onSupprimer={supprimer}
          onRelancer={relancer}
        />
      ) : (
        <OngletQuestions
          referentielsAttaches={referentielsAttaches}
          referentielsDisponibles={referentielsDisponibles}
          referentielChoisi={referentielChoisi}
          referentielActionEnCours={referentielActionEnCours}
          onChangerReferentielChoisi={setReferentielChoisi}
          onAttacher={attacher}
          onDetacher={detacher}
          chargementQuestions={chargementQuestions}
          details={detailsReferentiels}
          reponsesParQuestion={reponsesParQuestion}
          validationEnCoursId={validationEnCoursId}
          onValider={valider}
          reanalyseEnCours={declenchementReanalyseEnCours || appelOffre.statut === "en_cours"}
          onReanalyser={reanalyser}
        />
      )}
    </Layout>
  );
}
