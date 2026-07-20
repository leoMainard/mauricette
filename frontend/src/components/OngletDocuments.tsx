import { Upload } from "lucide-react";
import { useRef } from "react";
import type { DocumentDepose, DocumentTraitementRag } from "../api/types";
import { EXTENSIONS_DOCUMENTS_ACCEPTEES } from "../constantesDocuments";
import { ArborescenceDocuments } from "./ArborescenceDocuments";
import { ProgressionTraitementAo } from "./ProgressionTraitementAo";
import { SuiviDepot, type SuiviFichier } from "./SuiviDepot";

interface Props {
  documents: DocumentDepose[];
  suivis: SuiviFichier[];
  suppressionEnCours: Set<string>;
  traitements: Map<string, DocumentTraitementRag>;
  relanceEnCours: Set<string>;
  onAjouterFichiers: (fichiers: File[]) => void;
  onSupprimer: (document: DocumentDepose) => void;
  onRelancer: (document: DocumentDepose) => void;
}

/** Onglet "Documents" de la fiche AO : liste des documents + ajout compact. */
export function OngletDocuments({
  documents,
  suivis,
  suppressionEnCours,
  traitements,
  relanceEnCours,
  onAjouterFichiers,
  onSupprimer,
  onRelancer,
}: Props) {
  const entreeFichier = useRef<HTMLInputElement>(null);

  return (
    <div className="carte carte--documents">
      <div className="entete-page--avec-action">
        <h2>Documents du dossier {documents.length}</h2>
        <button type="button" className="bouton-fantome" onClick={() => entreeFichier.current?.click()}>
          <Upload size={15} style={{ marginRight: "4px" }} />
          Ajouter
        </button>
        <input
          ref={entreeFichier}
          type="file"
          multiple
          hidden
          accept={EXTENSIONS_DOCUMENTS_ACCEPTEES}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              onAjouterFichiers(Array.from(e.target.files));
            }
            e.target.value = "";
          }}
        />
      </div>
      <SuiviDepot suivis={suivis} />
      <ProgressionTraitementAo traitements={Array.from(traitements.values())} />
      <ArborescenceDocuments
        documents={documents}
        onSupprimer={onSupprimer}
        suppressionEnCours={suppressionEnCours}
        traitements={traitements}
        onRelancer={onRelancer}
        relanceEnCours={relanceEnCours}
      />
    </div>
  );
}
