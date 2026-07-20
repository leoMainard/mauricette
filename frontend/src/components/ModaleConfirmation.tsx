interface Props {
  titre: string;
  message: string;
  texteConfirmation?: string;
  texteAnnulation?: string;
  dangereux?: boolean;
  enCours?: boolean;
  erreur?: string | null;
  onConfirmer: () => void;
  onAnnuler: () => void;
}

/** Boîte de dialogue de confirmation générique, pour toute action à valider explicitement. */
export function ModaleConfirmation({
  titre,
  message,
  texteConfirmation = "Confirmer",
  texteAnnulation = "Annuler",
  dangereux = false,
  enCours = false,
  erreur = null,
  onConfirmer,
  onAnnuler,
}: Props) {
  return (
    <div className="modale-fond" onClick={onAnnuler}>
      <div
        className="modale-carte"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="modale-confirmation-titre"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modale-confirmation-titre">{titre}</h2>
        <p className="texte-discret">{message}</p>
        {erreur && <p className="message-erreur">{erreur}</p>}
        <div className="modale-actions">
          <button type="button" className="bouton-fantome" onClick={onAnnuler} disabled={enCours}>
            {texteAnnulation}
          </button>
          <button
            type="button"
            className={dangereux ? "bouton-danger" : undefined}
            onClick={onConfirmer}
            disabled={enCours}
          >
            {enCours ? "Suppression..." : texteConfirmation}
          </button>
        </div>
      </div>
    </div>
  );
}
