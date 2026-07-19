interface Props {
  coche: boolean;
  onChange: (valeur: boolean) => void;
  disabled?: boolean;
  libelle: string;
}

/** Interrupteur à bascule (case à cocher stylisée en pilule). */
export function Interrupteur({ coche, onChange, disabled, libelle }: Props) {
  return (
    <label className="interrupteur">
      <input
        type="checkbox"
        checked={coche}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        aria-label={libelle}
      />
      <span className="interrupteur__curseur" aria-hidden="true" />
    </label>
  );
}
