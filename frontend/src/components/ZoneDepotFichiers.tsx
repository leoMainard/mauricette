import { useRef, useState } from "react";
import { EXTENSIONS_DOCUMENTS_ACCEPTEES } from "../constantesDocuments";

interface Props {
  /** Appelé avec les fichiers ajoutés par glisser-déposer ou sélection manuelle. */
  onFichiersAjoutes: (fichiers: File[]) => void;
}

/**
 * Zone de glisser-déposer / sélection de fichiers.
 * Ne fait aucun envoi réseau : elle se contente de faire remonter les fichiers
 * choisis, qui restent en attente jusqu'à la création de l'Appel d'Offres.
 */
export function ZoneDepotFichiers({ onFichiersAjoutes }: Props) {
  const [survole, setSurvole] = useState(false);
  const entreeFichier = useRef<HTMLInputElement>(null);

  function ajouter(fichiers: FileList | null) {
    if (!fichiers || fichiers.length === 0) return;
    onFichiersAjoutes(Array.from(fichiers));
  }

  return (
    <div
      className={`zone-depot ${survole ? "zone-depot--survolee" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setSurvole(true);
      }}
      onDragLeave={() => setSurvole(false)}
      onDrop={(e) => {
        e.preventDefault();
        setSurvole(false);
        ajouter(e.dataTransfer.files);
      }}
      onClick={() => entreeFichier.current?.click()}
    >
      <p>Glissez-déposez vos documents ici (PDF, Word, Excel, images, zip...)</p>
      <p className="texte-discret">
        ou cliquez pour parcourir vos fichiers — un zip est automatiquement dézippé
      </p>
      <input
        ref={entreeFichier}
        type="file"
        multiple
        hidden
        accept={EXTENSIONS_DOCUMENTS_ACCEPTEES}
        onChange={(e) => {
          ajouter(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
