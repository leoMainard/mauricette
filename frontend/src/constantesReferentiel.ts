import { Award, BookOpen, Briefcase, Compass, Flag, Gem, Layers, Shield, Star, Target, Zap } from "lucide-react";
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

const ICONES_SECTION = [Award, BookOpen, Briefcase, Compass, Flag, Gem, Layers, Shield, Star, Target, Zap];

/** Icône de section aléatoire mais stable : dérivée de l'id, pas re-tirée à chaque rendu. */
export function iconeSection(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) | 0;
  }
  return ICONES_SECTION[Math.abs(hash) % ICONES_SECTION.length];
}
