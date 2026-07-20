interface Props {
  url: string;
}

/** Repli affiché quand le type de fichier n'a pas de rendu dédié (pptx, odt, txt, tiff...). */
export function ApercuNonDisponible({ url }: Props) {
  return (
    <div className="apercu-indisponible">
      <p>Aperçu non disponible pour ce type de fichier.</p>
      <a href={url} target="_blank" rel="noreferrer">
        Ouvrir dans un nouvel onglet
      </a>
    </div>
  );
}
