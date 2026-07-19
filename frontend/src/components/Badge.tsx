interface Props {
  statut: string;
  libelle: string;
}

/** Pastille de statut : point coloré + libellé, la couleur du point suit celle du texte. */
export function Badge({ statut, libelle }: Props) {
  return (
    <span className={`badge badge--${statut}`}>
      <span className="badge__point" aria-hidden="true" />
      {libelle}
    </span>
  );
}
