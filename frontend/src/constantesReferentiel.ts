import type { FormatReponse } from "./api/types";

/** Libellés et options du champ "format de réponse", partagés par les pages du référentiel. */
export const LIBELLES_FORMAT_REPONSE: Record<FormatReponse, string> = {
  texte_libre: "Texte",
  oui_non: "Oui / Non",
  montant: "Montant",
  date: "Date",
  pourcentage: "Pourcentage",
  liste: "Liste",
  autre: "Autre",
};

export const OPTIONS_FORMAT_REPONSE: FormatReponse[] = [
  "texte_libre",
  "oui_non",
  "montant",
  "date",
  "pourcentage",
  "liste",
  "autre",
];
