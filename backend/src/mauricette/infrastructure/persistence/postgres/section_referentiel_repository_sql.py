"""Adaptateur PostgreSQL du port `SectionReferentielRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import (
    section_referentiel_vers_entite,
    section_referentiel_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import SectionReferentielModele


class SectionReferentielRepositorySQL(SectionReferentielRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des sections."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, section: SectionReferentiel) -> None:
        self._session.add(section_referentiel_vers_modele(section))
        self._session.commit()

    def obtenir_par_id(self, section_id: UUID) -> SectionReferentiel | None:
        modele = self._session.get(SectionReferentielModele, section_id)
        return section_referentiel_vers_entite(modele) if modele else None

    def lister_par_referentiel(self, referentiel_id: UUID) -> list[SectionReferentiel]:
        requete = (
            select(SectionReferentielModele)
            .where(SectionReferentielModele.referentiel_id == referentiel_id)
            .order_by(SectionReferentielModele.ordre, SectionReferentielModele.nom)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [section_referentiel_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, section: SectionReferentiel) -> None:
        modele = self._session.get(SectionReferentielModele, section.id)
        if modele is None:
            raise ValueError(f"Section introuvable : {section.id}")
        modele.nom = section.nom
        modele.ordre = section.ordre
        self._session.commit()

    def supprimer(self, section_id: UUID) -> None:
        modele = self._session.get(SectionReferentielModele, section_id)
        if modele is None:
            raise ValueError(f"Section introuvable : {section_id}")
        self._session.delete(modele)
        self._session.commit()

    def compter_par_referentiel(self) -> dict[UUID, int]:
        requete = select(
            SectionReferentielModele.referentiel_id, func.count(SectionReferentielModele.id)
        ).group_by(SectionReferentielModele.referentiel_id)
        resultats = self._session.execute(requete).all()
        return {referentiel_id: nombre for referentiel_id, nombre in resultats}
