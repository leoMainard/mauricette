import type { DocumentDepose } from "../api/types";

interface Props {
  documents: DocumentDepose[];
  /** Si fourni, affiche un bouton de suppression sur chaque fichier. */
  onSupprimer?: (document: DocumentDepose) => void;
  /** Documents en cours de suppression (affiche un état désactivé). */
  suppressionEnCours?: Set<string>;
}

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
}: {
  noeud: NoeudArbre;
  profondeur: number;
  onSupprimer?: (document: DocumentDepose) => void;
  suppressionEnCours?: Set<string>;
}) {
  const style = { paddingLeft: `${profondeur * 20}px` };

  if (noeud.document) {
    const document = noeud.document;
    const enCoursDeSuppression = suppressionEnCours?.has(document.id) ?? false;
    return (
      <li className="arbre-noeud arbre-noeud--fichier" style={style}>
        <span className="arbre-noeud__icone">📄</span>
        <span className="arbre-noeud__nom">{noeud.nom}</span>
        <span className="texte-discret">{formaterTaille(document.taille_octets)}</span>
        <span className={`badge badge--${document.statut}`}>{document.statut}</span>
        {onSupprimer && (
          <button
            type="button"
            onClick={() => onSupprimer(document)}
            disabled={enCoursDeSuppression}
            aria-label={`Supprimer ${noeud.nom}`}
          >
            {enCoursDeSuppression ? "..." : "Supprimer"}
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
export function ArborescenceDocuments({ documents, onSupprimer, suppressionEnCours }: Props) {
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
        />
      ))}
    </ul>
  );
}
