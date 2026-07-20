import { renderAsync } from "docx-preview";
import { useEffect, useRef, useState } from "react";

interface Props {
  url: string;
}

/** Aperçu DOCX rendu côté client via `docx-preview` (préserve la mise en page). */
export function ApercuDocx({ url }: Props) {
  const conteneur = useRef<HTMLDivElement>(null);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;
    setErreur(null);

    fetch(url)
      .then((reponse) => reponse.blob())
      .then((blob) => {
        if (annule || !conteneur.current) return;
        return renderAsync(blob, conteneur.current);
      })
      .catch((e) => {
        console.error("Aperçu DOCX : échec du chargement/rendu", e);
        if (!annule) setErreur("Impossible d'afficher ce document.");
      });

    return () => {
      annule = true;
    };
  }, [url]);

  if (erreur) return <p className="message-erreur">{erreur}</p>;
  return <div ref={conteneur} className="apercu-docx" />;
}
