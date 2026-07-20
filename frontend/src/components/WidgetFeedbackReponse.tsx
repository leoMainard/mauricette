import { AlertTriangle, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import type { DetailFeedbackReponse } from "../api/feedbackApi";
import type { Avis, FeedbackReponse, TypeErreurFeedback } from "../api/types";

interface Props {
  feedback: FeedbackReponse | null;
  contenuReponseActuel: string | null;
  enCours: boolean;
  onEnregistrer: (detail: DetailFeedbackReponse) => void;
}

const LIBELLES_TYPE_ERREUR: Record<TypeErreurFeedback, string> = {
  information_incorrecte: "Information incorrecte",
  information_incomplete: "Information incomplète",
  mauvaise_source: "Mauvaise source citée",
  source_manquante: "Source manquante",
  format_inadapte: "Format de réponse inadapté",
  autre: "Autre",
};

/** Widget de feedback par réponse : pouce haut/bas rapide + détail optionnel. */
export function WidgetFeedbackReponse({
  feedback,
  contenuReponseActuel,
  enCours,
  onEnregistrer,
}: Props) {
  const [detailOuvert, setDetailOuvert] = useState(false);
  const [sourceAttendue, setSourceAttendue] = useState(feedback?.source_attendue ?? "");
  const [citationAttendue, setCitationAttendue] = useState(feedback?.citation_attendue ?? "");
  const [typeErreur, setTypeErreur] = useState<TypeErreurFeedback | "">(feedback?.type_erreur ?? "");
  const [detailsErreur, setDetailsErreur] = useState(feedback?.details_erreur ?? "");

  const reponseModifieeDepuis =
    feedback?.contenu_reponse_snapshot != null &&
    feedback.contenu_reponse_snapshot !== contenuReponseActuel;

  function cliquerPouce(avis: Avis) {
    const nouvelAvis = feedback?.avis === avis ? null : avis;
    onEnregistrer({
      avis: nouvelAvis,
      commentaire: feedback?.commentaire ?? null,
      source_attendue: feedback?.source_attendue ?? null,
      citation_attendue: feedback?.citation_attendue ?? null,
      type_erreur: feedback?.type_erreur ?? null,
      details_erreur: feedback?.details_erreur ?? null,
    });
  }

  function enregistrerDetail() {
    onEnregistrer({
      avis: feedback?.avis ?? null,
      source_attendue: sourceAttendue.trim() || null,
      citation_attendue: citationAttendue.trim() || null,
      type_erreur: typeErreur || null,
      details_erreur: detailsErreur.trim() || null,
    });
    setDetailOuvert(false);
  }

  return (
    <div className="widget-feedback-reponse">
      <div className="boutons-pouce">
        <button
          type="button"
          className={`bouton-icone bouton-pouce${feedback?.avis === "positif" ? " bouton-pouce--actif-positif" : ""}`}
          onClick={() => cliquerPouce("positif")}
          disabled={enCours}
          title="Réponse utile"
          aria-label="Feedback positif sur cette réponse"
        >
          <ThumbsUp size={13} />
        </button>
        <button
          type="button"
          className={`bouton-icone bouton-pouce${feedback?.avis === "negatif" ? " bouton-pouce--actif-negatif" : ""}`}
          onClick={() => cliquerPouce("negatif")}
          disabled={enCours}
          title="Réponse pas utile"
          aria-label="Feedback négatif sur cette réponse"
        >
          <ThumbsDown size={13} />
        </button>
        <button
          type="button"
          className="bouton-fantome bouton-fantome--discret"
          onClick={() => setDetailOuvert((v) => !v)}
        >
          Détailler
        </button>
        {reponseModifieeDepuis && (
          <span className="puce-reponse-modifiee" title="Le contenu de la réponse a changé depuis ce retour">
            <AlertTriangle size={11} />
            Réponse modifiée depuis
          </span>
        )}
      </div>

      {detailOuvert && (
        <div className="formulaire-detail-feedback">
          <label>
            Source attendue
            <input
              type="text"
              value={sourceAttendue}
              onChange={(e) => setSourceAttendue(e.target.value)}
              placeholder="ex : CCTP, page 4"
              disabled={enCours}
            />
          </label>
          <label>
            Citation attendue
            <input
              type="text"
              value={citationAttendue}
              onChange={(e) => setCitationAttendue(e.target.value)}
              placeholder="ex : passage exact attendu"
              disabled={enCours}
            />
          </label>
          <label>
            Type d'erreur
            <select
              value={typeErreur}
              onChange={(e) => setTypeErreur(e.target.value as TypeErreurFeedback | "")}
              disabled={enCours}
            >
              <option value="">Sélectionner...</option>
              {Object.entries(LIBELLES_TYPE_ERREUR).map(([valeur, libelle]) => (
                <option key={valeur} value={valeur}>
                  {libelle}
                </option>
              ))}
            </select>
          </label>
          <label>
            Précisions
            <textarea
              value={detailsErreur}
              onChange={(e) => setDetailsErreur(e.target.value)}
              rows={2}
              disabled={enCours}
            />
          </label>
          <button type="button" className="bouton-fantome" onClick={enregistrerDetail} disabled={enCours}>
            Enregistrer
          </button>
        </div>
      )}
    </div>
  );
}
