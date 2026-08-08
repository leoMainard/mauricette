import { ChevronDown, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { DocumentDepose } from "../api/types";

interface Props {
  documents: DocumentDepose[];
  valeur: string[];
  onChange: (idsDocuments: string[]) => void;
  disabled?: boolean;
}

/** Sélecteur de un ou plusieurs documents parmi ceux déposés sur l'AO, façon
 * `st.multiselect` : les documents choisis apparaissent en pastilles dans le
 * champ lui-même, et une liste déroulante filtrable par texte propose les
 * documents restants. */
export function SelecteurDocuments({ documents, valeur, onChange, disabled = false }: Props) {
  const [recherche, setRecherche] = useState("");
  const [ouvert, setOuvert] = useState(false);
  const conteneurRef = useRef<HTMLDivElement>(null);
  const entreeRef = useRef<HTMLInputElement>(null);

  const documentsParId = useMemo(() => {
    const map = new Map<string, DocumentDepose>();
    for (const document of documents) map.set(document.id, document);
    return map;
  }, [documents]);

  const optionsDisponibles = useMemo(() => {
    const terme = recherche.trim().toLowerCase();
    return documents
      .filter((document) => !valeur.includes(document.id))
      .filter((document) => !terme || document.nom_original.toLowerCase().includes(terme));
  }, [documents, valeur, recherche]);

  useEffect(() => {
    function surClicExterieur(e: MouseEvent) {
      if (conteneurRef.current && !conteneurRef.current.contains(e.target as Node)) {
        setOuvert(false);
      }
    }
    document.addEventListener("mousedown", surClicExterieur);
    return () => document.removeEventListener("mousedown", surClicExterieur);
  }, []);

  function ajouter(idDocument: string) {
    onChange([...valeur, idDocument]);
    setRecherche("");
    entreeRef.current?.focus();
  }

  function retirer(idDocument: string) {
    onChange(valeur.filter((id) => id !== idDocument));
  }

  function surTouche(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape") {
      setOuvert(false);
      entreeRef.current?.blur();
    } else if (e.key === "Backspace" && recherche === "" && valeur.length > 0) {
      retirer(valeur[valeur.length - 1]);
    }
  }

  return (
    <div className="selecteur-documents" ref={conteneurRef}>
      <div
        className={`selecteur-documents__controle${disabled ? " selecteur-documents__controle--desactive" : ""}`}
        onClick={() => {
          if (disabled) return;
          setOuvert(true);
          entreeRef.current?.focus();
        }}
      >
        {valeur.map((id) => {
          const document = documentsParId.get(id);
          return (
            <span key={id} className="pastille-document-selectionne" title={document?.nom_original}>
              {document?.nom_original ?? "Document supprimé"}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  retirer(id);
                }}
                disabled={disabled}
                aria-label={`Retirer ${document?.nom_original ?? "ce document"}`}
              >
                <X size={12} />
              </button>
            </span>
          );
        })}
        <input
          ref={entreeRef}
          type="text"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
          onFocus={() => setOuvert(true)}
          onKeyDown={surTouche}
          placeholder={valeur.length === 0 ? "Choisir un ou plusieurs documents..." : ""}
          disabled={disabled}
        />
        <ChevronDown
          size={16}
          className={`selecteur-documents__chevron${ouvert ? " selecteur-documents__chevron--ouvert" : ""}`}
          aria-hidden="true"
        />
      </div>

      {ouvert && !disabled && (
        // onMouseDown (pas onClick) + preventDefault : empêche le mousedown sur une option
        // de faire perdre le focus au champ de recherche avant que le clic ne soit traité.
        <div className="selecteur-documents__menu" onMouseDown={(e) => e.preventDefault()}>
          {optionsDisponibles.length === 0 ? (
            <p className="selecteur-documents__vide">
              {documents.length === 0 ? "Aucun document déposé sur cet AO." : "Aucun document ne correspond."}
            </p>
          ) : (
            optionsDisponibles.map((document) => (
              <div
                key={document.id}
                className="selecteur-documents__option"
                onClick={() => ajouter(document.id)}
                title={document.nom_original}
              >
                {document.nom_original}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
