import { AlertTriangle, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import type { DetailFeedbackReponse } from "../api/feedbackApi";
import type { Avis, DocumentDepose, FeedbackReponse, TypeErreurFeedback } from "../api/types";
import { SelecteurDocuments } from "./SelecteurDocuments";

interface Props {
  feedback: FeedbackReponse | null;
  contenuReponseActuel: string | null;
  documents: DocumentDepose[];
  enCours: boolean;
  onEnregistrer: (detail: DetailFeedbackReponse) => void;
}

export const LIBELLES_TYPE_ERREUR: Record<TypeErreurFeedback, string> = {
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
  documents,
  enCours,
  onEnregistrer,
}: Props) {
  const [detailOuvert, setDetailOuvert] = useState(false);
  const [sourcesAttendues, setSourcesAttendues] = useState<string[]>(
    feedback?.sources_attendues_ids ?? [],
  );
  const [citationAttendue, setCitationAttendue] = useState(feedback?.citation_attendue ?? "");
  const [typesErreur, setTypesErreur] = useState<TypeErreurFeedback[]>(feedback?.types_erreur ?? []);
  const [detailsErreur, setDetailsErreur] = useState(feedback?.details_erreur ?? "");

  const reponseModifieeDepuis =
    feedback?.contenu_reponse_snapshot != null &&
    feedback.contenu_reponse_snapshot !== contenuReponseActuel;

  function cliquerPouce(avis: Avis) {
    const nouvelAvis = feedback?.avis === avis ? null : avis;
    onEnregistrer({
      avis: nouvelAvis,
      commentaire: feedback?.commentaire ?? null,
      sources_attendues_ids: feedback?.sources_attendues_ids ?? [],
      citation_attendue: feedback?.citation_attendue ?? null,
      types_erreur: feedback?.types_erreur ?? [],
      details_erreur: feedback?.details_erreur ?? null,
    });
  }

  function basculerTypeErreur(type: TypeErreurFeedback) {
    setTypesErreur((types) =>
      types.includes(type) ? types.filter((t) => t !== type) : [...types, type],
    );
  }

  function enregistrerDetail() {
    onEnregistrer({
      avis: feedback?.avis ?? null,
      sources_attendues_ids: sourcesAttendues,
      citation_attendue: citationAttendue.trim() || null,
      types_erreur: typesErreur,
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
          <div className="champ-detail-feedback">
            <span className="champ-detail-feedback__libelle">Source(s) attendue(s)</span>
            <SelecteurDocuments
              documents={documents}
              valeur={sourcesAttendues}
              onChange={setSourcesAttendues}
              disabled={enCours}
            />
          </div>
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
            Type(s) d'erreur
            <div className="pastilles-filtre">
              {Object.entries(LIBELLES_TYPE_ERREUR).map(([valeur, libelle]) => (
                <button
                  key={valeur}
                  type="button"
                  className={`pastille-filtre${
                    typesErreur.includes(valeur as TypeErreurFeedback) ? " pastille-filtre--active" : ""
                  }`}
                  onClick={() => basculerTypeErreur(valeur as TypeErreurFeedback)}
                  disabled={enCours}
                  aria-pressed={typesErreur.includes(valeur as TypeErreurFeedback)}
                >
                  {libelle}
                </button>
              ))}
            </div>
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
