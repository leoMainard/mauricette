import { X } from "lucide-react";
import { urlContenuDocument } from "../../api/appelsOffreApi";
import { ApercuDocx } from "./ApercuDocx";
import { ApercuExcel } from "./ApercuExcel";
import { ApercuImage } from "./ApercuImage";
import { ApercuNonDisponible } from "./ApercuNonDisponible";
import { ApercuPdf } from "./ApercuPdf";

export interface DocumentAPercevoir {
  documentId: string;
  nomOriginal: string;
  typeMime: string;
  pageInitiale?: number | null;
}

interface Props {
  appelOffreId: string;
  /** null => panneau fermé, rien n'est monté. */
  document: DocumentAPercevoir | null;
  onFermer: () => void;
}

const TYPE_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
const TYPES_EXCEL = new Set([
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.ms-excel",
]);

/** Devine le type réel à partir de l'extension, pour les navigateurs qui envoient
 * un type MIME générique (`application/octet-stream`) au dépôt du fichier. */
function typeDepuisExtension(nom: string): string | null {
  const extension = nom.slice(nom.lastIndexOf(".")).toLowerCase();
  switch (extension) {
    case ".pdf":
      return "application/pdf";
    case ".docx":
      return TYPE_DOCX;
    case ".xlsx":
    case ".xls":
      return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
    case ".jpg":
    case ".jpeg":
      return "image/jpeg";
    case ".png":
      return "image/png";
    case ".gif":
      return "image/gif";
    case ".webp":
      return "image/webp";
    case ".bmp":
      return "image/bmp";
    default:
      return null;
  }
}

function rendreApercu(document: DocumentAPercevoir, url: string) {
  const typeGenerique = !document.typeMime || document.typeMime === "application/octet-stream";
  const type = typeGenerique
    ? (typeDepuisExtension(document.nomOriginal) ?? document.typeMime)
    : document.typeMime;

  if (type === "application/pdf") {
    return <ApercuPdf url={url} page={document.pageInitiale} />;
  }
  if (type.startsWith("image/") && type !== "image/tiff") {
    return <ApercuImage url={url} nom={document.nomOriginal} />;
  }
  if (type === TYPE_DOCX) {
    return <ApercuDocx url={url} />;
  }
  if (TYPES_EXCEL.has(type)) {
    return <ApercuExcel url={url} />;
  }
  return <ApercuNonDisponible url={url} />;
}

/** Panneau d'aperçu de document, ancré à droite, non bloquant (le reste de la page reste utilisable). */
export function PanneauApercuDocument({ appelOffreId, document, onFermer }: Props) {
  if (!document) return null;
  const url = urlContenuDocument(appelOffreId, document.documentId);

  return (
    <div className="panneau-apercu">
      <div className="panneau-apercu__entete">
        <span className="panneau-apercu__nom" title={document.nomOriginal}>
          {document.nomOriginal}
        </span>
        <button
          type="button"
          className="bouton-icone"
          onClick={onFermer}
          title="Fermer"
          aria-label="Fermer l'aperçu"
        >
          <X size={18} />
        </button>
      </div>
      <div className="panneau-apercu__corps">{rendreApercu(document, url)}</div>
    </div>
  );
}
