interface Props {
  url: string;
  page?: number | null;
}

/** Aperçu PDF via le lecteur natif du navigateur (iframe), sans bibliothèque. */
export function ApercuPdf({ url, page }: Props) {
  const source = page ? `${url}#page=${page}` : url;
  return <iframe src={source} title="Aperçu du document" />;
}
