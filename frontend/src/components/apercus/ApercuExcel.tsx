import { useEffect, useState } from "react";
import { read, utils } from "xlsx";

interface Props {
  url: string;
}

/** Aperçu Excel (première feuille) : parsé côté client avec SheetJS, rendu en <table> React. */
export function ApercuExcel({ url }: Props) {
  const [lignes, setLignes] = useState<unknown[][] | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;
    setLignes(null);
    setErreur(null);

    fetch(url)
      .then((reponse) => reponse.arrayBuffer())
      .then((buffer) => {
        if (annule) return;
        const classeur = read(buffer, { type: "array" });
        const premiereFeuille = classeur.Sheets[classeur.SheetNames[0]];
        const donnees = utils.sheet_to_json(premiereFeuille, { header: 1, defval: "" }) as unknown[][];
        setLignes(donnees);
      })
      .catch((e) => {
        console.error("Aperçu Excel : échec du chargement/parsing", e);
        if (!annule) setErreur("Impossible d'afficher ce fichier.");
      });

    return () => {
      annule = true;
    };
  }, [url]);

  if (erreur) return <p className="message-erreur">{erreur}</p>;
  if (!lignes) return <p className="texte-discret">Chargement...</p>;

  return (
    <table className="apercu-excel">
      <tbody>
        {lignes.map((ligne, i) => (
          <tr key={i}>
            {ligne.map((cellule, j) => (
              <td key={j}>{String(cellule)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
