interface Props {
  fichiers: File[];
  onRetirer: (index: number) => void;
}

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

/** Repère les fichiers dont le nom ET la taille apparaissent plusieurs fois dans la liste.
 *
 * Un simple indice visuel avant l'envoi : la détection fiable (par contenu réel,
 * via hash) est faite côté serveur au moment du dépôt.
 */
function reperer_doublons_probables(fichiers: File[]): boolean[] {
  const occurrences = new Map<string, number>();
  for (const fichier of fichiers) {
    const cle = `${fichier.name}_${fichier.size}`;
    occurrences.set(cle, (occurrences.get(cle) ?? 0) + 1);
  }
  return fichiers.map((fichier) => (occurrences.get(`${fichier.name}_${fichier.size}`) ?? 0) > 1);
}

/** Liste des fichiers en attente d'envoi, avec possibilité de les retirer avant la création de l'AO. */
export function ListeFichiersEnAttente({ fichiers, onRetirer }: Props) {
  if (fichiers.length === 0) {
    return null;
  }

  const doublonsProbables = reperer_doublons_probables(fichiers);

  return (
    <ul className="liste-fichiers-attente">
      {fichiers.map((fichier, index) => (
        <li key={`${fichier.name}-${fichier.size}-${index}`} className="fichier-attente">
          <span className="fichier-attente__nom">
            {fichier.name}
            {doublonsProbables[index] && (
              <span className="badge badge--en_attente" title="Un autre fichier du même nom et de la même taille est déjà dans la liste">
                doublon possible
              </span>
            )}
          </span>
          <span className="texte-discret">{formaterTaille(fichier.size)}</span>
          <button type="button" onClick={() => onRetirer(index)} aria-label={`Retirer ${fichier.name}`}>
            Retirer
          </button>
        </li>
      ))}
    </ul>
  );
}
