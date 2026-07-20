import { RotateCw, Trash2 } from "lucide-react";
import type { DocumentDepose, DocumentTraitementRag, StatutDocument } from "../api/types";
import { Badge } from "./Badge";
import { BadgeEtapeTraitement } from "./BadgeEtapeTraitement";

interface Props {
  documents: DocumentDepose[];
  /** Si fourni, affiche un bouton de suppression sur chaque fichier. */
  onSupprimer?: (document: DocumentDepose) => void;
  /** Documents en cours de suppression (affiche un état désactivé). */
  suppressionEnCours?: Set<string>;
  /** Suivi du pipeline RAG par document (id -> suivi), pour afficher la pastille d'étape. */
  traitements?: Map<string, DocumentTraitementRag>;
  /** Si fourni (avec `traitements`), affiche un bouton de relance sur les documents en échec. */
  onRelancer?: (document: DocumentDepose) => void;
  /** Documents dont la relance est en cours (affiche un état désactivé). */
  relanceEnCours?: Set<string>;
  /** Si fourni, un clic sur un fichier ouvre son aperçu. */
  onOuvrirApercu?: (document: DocumentDepose) => void;
}

/** Premier message d'erreur non nul parmi les 3 étapes du pipeline, pour l'afficher en info-bulle. */
function messageErreurTraitement(traitement: DocumentTraitementRag): string | undefined {
  return (
    traitement.extraction.message_erreur ??
    traitement.decoupage.message_erreur ??
    traitement.embedding.message_erreur ??
    undefined
  );
}

const LIBELLES_STATUT: Record<StatutDocument, string> = {
  en_attente: "En attente",
  televerse: "Déposé",
  en_erreur: "Erreur",
  traite: "Traité",
};

interface NoeudArbre {
  nom: string;
  enfants: Map<string, NoeudArbre>;
  document?: DocumentDepose;
}

/** Construit un arbre dossiers/fichiers à partir du chemin relatif (nom_original) de chaque document. */
function construireArbre(documents: DocumentDepose[]): NoeudArbre {
  const racine: NoeudArbre = { nom: "", enfants: new Map() };

  for (const document of documents) {
    const segments = document.nom_original.split("/").filter((segment) => segment.length > 0);
    let noeudCourant = racine;

    segments.forEach((segment, index) => {
      if (!noeudCourant.enfants.has(segment)) {
        noeudCourant.enfants.set(segment, { nom: segment, enfants: new Map() });
      }
      noeudCourant = noeudCourant.enfants.get(segment)!;
      if (index === segments.length - 1) {
        noeudCourant.document = document;
      }
    });
  }

  return racine;
}

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

function trierEnfants(noeud: NoeudArbre): NoeudArbre[] {
  return Array.from(noeud.enfants.values()).sort((a, b) => {
    const aEstDossier = a.document === undefined;
    const bEstDossier = b.document === undefined;
    if (aEstDossier !== bEstDossier) return aEstDossier ? -1 : 1;
    return a.nom.localeCompare(b.nom);
  });
}

function NoeudArborescence({
  noeud,
  profondeur,
  onSupprimer,
  suppressionEnCours,
  traitements,
  onRelancer,
  relanceEnCours,
  onOuvrirApercu,
}: {
  noeud: NoeudArbre;
  profondeur: number;
  onSupprimer?: (document: DocumentDepose) => void;
  suppressionEnCours?: Set<string>;
  traitements?: Map<string, DocumentTraitementRag>;
  onRelancer?: (document: DocumentDepose) => void;
  relanceEnCours?: Set<string>;
  onOuvrirApercu?: (document: DocumentDepose) => void;
}) {
  const style = { paddingLeft: `${profondeur * 20}px` };

  if (noeud.document) {
    const document = noeud.document;
    const enCoursDeSuppression = suppressionEnCours?.has(document.id) ?? false;
    const traitement = traitements?.get(document.id);
    const enCoursDeRelance = relanceEnCours?.has(document.id) ?? false;
    return (
      <li
        className="arbre-noeud arbre-noeud--fichier"
        style={style}
        onClick={() => onOuvrirApercu?.(document)}
        role={onOuvrirApercu ? "button" : undefined}
        tabIndex={onOuvrirApercu ? 0 : undefined}
        onKeyDown={(e) => {
          if (onOuvrirApercu && e.key === "Enter") onOuvrirApercu(document);
        }}
      >
        <span className="arbre-noeud__icone">📄</span>
        <span className="arbre-noeud__nom">{noeud.nom}</span>
        <span className="texte-discret">{formaterTaille(document.taille_octets)}</span>
        <Badge statut={document.statut} libelle={LIBELLES_STATUT[document.statut]} />
        {traitement && <BadgeEtapeTraitement statut={traitement.statut_global} />}
        {traitement?.statut_global === "echec" && onRelancer && (
          <button
            type="button"
            className="bouton-icone"
            onClick={(e) => {
              e.stopPropagation();
              onRelancer(document);
            }}
            disabled={enCoursDeRelance}
            title={messageErreurTraitement(traitement) ?? "Relancer le traitement"}
            aria-label={`Relancer le traitement de ${noeud.nom}`}
          >
            <RotateCw size={15} />
          </button>
        )}
        {onSupprimer && (
          <button
            type="button"
            className="bouton-icone bouton-icone--annuler"
            onClick={(e) => {
              e.stopPropagation();
              onSupprimer(document);
            }}
            disabled={enCoursDeSuppression}
            title="Supprimer"
            aria-label={`Supprimer ${noeud.nom}`}
          >
            <Trash2 size={15} />
          </button>
        )}
      </li>
    );
  }

  return (
    <>
      <li className="arbre-noeud arbre-noeud--dossier" style={style}>
        <span className="arbre-noeud__icone">📁</span>
        <span className="arbre-noeud__nom">{noeud.nom}</span>
      </li>
      {trierEnfants(noeud).map((enfant) => (
        <NoeudArborescence
          key={enfant.nom}
          noeud={enfant}
          profondeur={profondeur + 1}
          onSupprimer={onSupprimer}
          suppressionEnCours={suppressionEnCours}
          traitements={traitements}
          onRelancer={onRelancer}
          relanceEnCours={relanceEnCours}
          onOuvrirApercu={onOuvrirApercu}
        />
      ))}
    </>
  );
}

/**
 * Affiche les documents d'un AO sous forme d'arborescence, en reconstituant la
 * structure de dossiers d'origine (utile pour un gros zip : on retrouve les
 * fichiers là où ils étaient rangés).
 */
export function ArborescenceDocuments({
  documents,
  onSupprimer,
  suppressionEnCours,
  traitements,
  onRelancer,
  relanceEnCours,
  onOuvrirApercu,
}: Props) {
  if (documents.length === 0) {
    return <p className="texte-discret">Aucun document pour le moment.</p>;
  }

  const racine = construireArbre(documents);

  return (
    <ul className="arborescence">
      {trierEnfants(racine).map((enfant) => (
        <NoeudArborescence
          key={enfant.nom}
          noeud={enfant}
          profondeur={0}
          onSupprimer={onSupprimer}
          suppressionEnCours={suppressionEnCours}
          traitements={traitements}
          onRelancer={onRelancer}
          relanceEnCours={relanceEnCours}
          onOuvrirApercu={onOuvrirApercu}
        />
      ))}
    </ul>
  );
}
