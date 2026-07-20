interface Props {
  url: string;
  nom: string;
}

/** Aperçu image via une simple balise <img>, sans bibliothèque. */
export function ApercuImage({ url, nom }: Props) {
  return <img src={url} alt={nom} />;
}
