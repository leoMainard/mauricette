import { Pencil, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import type { Avis, FeedbackGeneral } from "../api/types";

interface Props {
  feedback: FeedbackGeneral | null;
  enCours: boolean;
  onEnregistrer: (avis: Avis | null, commentaire: string | null) => void;
}

/** Widget de feedback général par AO : pouce haut/bas + commentaire toujours visible, éditable. */
export function WidgetFeedbackGeneral({ feedback, enCours, onEnregistrer }: Props) {
  const [enEdition, setEnEdition] = useState(false);
  const [commentaireLocal, setCommentaireLocal] = useState(feedback?.commentaire ?? "");

  function cliquerPouce(avis: Avis) {
    const nouvelAvis = feedback?.avis === avis ? null : avis;
    onEnregistrer(nouvelAvis, feedback?.commentaire ?? null);
  }

  function ouvrirEdition() {
    setCommentaireLocal(feedback?.commentaire ?? "");
    setEnEdition(true);
  }

  function envoyerCommentaire() {
    onEnregistrer(feedback?.avis ?? null, commentaireLocal.trim() || null);
    setEnEdition(false);
  }

  function annulerEdition() {
    setCommentaireLocal(feedback?.commentaire ?? "");
    setEnEdition(false);
  }

  return (
    <div className="widget-feedback-general">
      <span className="widget-feedback-general__question">Cette analyse t'aide ?</span>
      <div className="boutons-pouce">
        <button
          type="button"
          className={`bouton-icone bouton-pouce${feedback?.avis === "positif" ? " bouton-pouce--actif-positif" : ""}`}
          onClick={() => cliquerPouce("positif")}
          disabled={enCours}
          title="Oui"
          aria-label="Feedback positif"
        >
          <ThumbsUp size={15} />
        </button>
        <button
          type="button"
          className={`bouton-icone bouton-pouce${feedback?.avis === "negatif" ? " bouton-pouce--actif-negatif" : ""}`}
          onClick={() => cliquerPouce("negatif")}
          disabled={enCours}
          title="Non"
          aria-label="Feedback négatif"
        >
          <ThumbsDown size={15} />
        </button>
      </div>

      {enEdition ? (
        <div className="widget-feedback-general__commentaire">
          <textarea
            value={commentaireLocal}
            onChange={(e) => setCommentaireLocal(e.target.value)}
            placeholder="Commentaire (optionnel)"
            rows={2}
            disabled={enCours}
            autoFocus
          />
          <div className="widget-feedback-general__commentaire-actions">
            <button type="button" className="bouton-fantome" onClick={annulerEdition} disabled={enCours}>
              Annuler
            </button>
            <button type="button" onClick={envoyerCommentaire} disabled={enCours}>
              Envoyer
            </button>
          </div>
        </div>
      ) : (
        <div className="widget-feedback-general__commentaire-affichage">
          {feedback?.commentaire ? (
            <p className="texte-discret">{feedback.commentaire}</p>
          ) : (
            <p className="texte-discret">Aucun commentaire.</p>
          )}
          <button
            type="button"
            className="bouton-icone"
            onClick={ouvrirEdition}
            disabled={enCours}
            title="Éditer le commentaire"
            aria-label="Éditer le commentaire"
          >
            <Pencil size={13} />
          </button>
        </div>
      )}
    </div>
  );
}
