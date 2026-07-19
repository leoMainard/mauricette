import type { DocumentDepose } from "../api/types";

interface Props {
  documents: DocumentDepose[];
}

const LIBELLES_STATUT: Record<DocumentDepose["statut"], string> = {
  en_attente: "En attente",
  televerse: "Déposé",
  en_erreur: "Erreur",
  traite: "Traité",
};

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

/** Liste des documents déjà déposés pour l'Appel d'Offres courant. */
export function ListeDocuments({ documents }: Props) {
  if (documents.length === 0) {
    return null;
  }

  return (
    <div className="carte">
      <h2>Documents déposés ({documents.length})</h2>
      <table className="table-documents">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Taille</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => (
            <tr key={document.id}>
              <td>{document.nom_original}</td>
              <td>{formaterTaille(document.taille_octets)}</td>
              <td>
                <span className={`badge badge--${document.statut}`}>
                  {LIBELLES_STATUT[document.statut]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
