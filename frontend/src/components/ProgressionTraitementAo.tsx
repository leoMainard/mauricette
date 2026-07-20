import type { DocumentTraitementRag } from "../api/types";

interface Props {
  traitements: DocumentTraitementRag[];
}

/** Résumé du pipeline RAG pour tous les documents d'un AO (ex: "3/5 traités, 1 en erreur"). */
export function ProgressionTraitementAo({ traitements }: Props) {
  if (traitements.length === 0) return null;

  const reussis = traitements.filter((t) => t.statut_global === "reussi").length;
  const echecs = traitements.filter((t) => t.statut_global === "echec").length;
  const enCours = traitements.filter(
    (t) => t.statut_global === "en_cours" || t.statut_global === "en_attente",
  ).length;

  return (
    <div className="progression-traitement">
      <span>
        {reussis}/{traitements.length} document{traitements.length > 1 ? "s" : ""} traité
        {reussis > 1 ? "s" : ""} par l'IA
      </span>
      {enCours > 0 && (
        <span className="progression-traitement__badge progression-traitement__badge--cours">
          {enCours} en cours
        </span>
      )}
      {echecs > 0 && (
        <span className="progression-traitement__badge progression-traitement__badge--erreur">
          {echecs} en erreur
        </span>
      )}
    </div>
  );
}
