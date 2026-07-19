"""Adaptateur PostgreSQL du port `ReferentielRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    referentiel_vers_entite,
    referentiel_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import ReferentielModele


class ReferentielRepositorySQL(ReferentielRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des référentiels."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, referentiel: Referentiel) -> None:
        self._session.add(referentiel_vers_modele(referentiel))
        self._session.commit()

    def obtenir_par_id(self, referentiel_id: UUID) -> Referentiel | None:
        modele = self._session.get(ReferentielModele, referentiel_id)
        return referentiel_vers_entite(modele) if modele else None

    def lister_tous(self, terme_recherche: str | None = None) -> list[Referentiel]:
        requete = select(ReferentielModele).order_by(ReferentielModele.nom)
        if terme_recherche:
            requete = requete.where(ReferentielModele.nom.ilike(f"%{terme_recherche}%"))
        modeles = self._session.execute(requete).scalars().all()
        return [referentiel_vers_entite(modele) for modele in modeles]

    def lister_actifs_par_defaut(self) -> list[Referentiel]:
        requete = select(ReferentielModele).where(ReferentielModele.actif_par_defaut.is_(True))
        modeles = self._session.execute(requete).scalars().all()
        return [referentiel_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, referentiel: Referentiel) -> None:
        modele = self._session.get(ReferentielModele, referentiel.id)
        if modele is None:
            raise ValueError(f"Référentiel introuvable : {referentiel.id}")
        modele.nom = referentiel.nom
        modele.description = referentiel.description
        modele.actif_par_defaut = referentiel.actif_par_defaut
        modele.date_maj = referentiel.date_maj
        self._session.commit()

    def supprimer(self, referentiel_id: UUID) -> None:
        modele = self._session.get(ReferentielModele, referentiel_id)
        if modele is None:
            raise ValueError(f"Référentiel introuvable : {referentiel_id}")
        self._session.delete(modele)
        self._session.commit()
