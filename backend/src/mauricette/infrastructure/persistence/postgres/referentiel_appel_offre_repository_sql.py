"""Adaptateur PostgreSQL du port `ReferentielAppelOffreRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import referentiel_vers_entite
from mauricette.infrastructure.persistence.postgres.modeles import (
    AppelOffreReferentielModele,
    QuestionReferentielModele,
    ReferentielModele,
    SectionReferentielModele,
)


class ReferentielAppelOffreRepositorySQL(ReferentielAppelOffreRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du rattachement référentiel ↔ AO."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def attacher(self, appel_offre_id: UUID, referentiel_id: UUID) -> None:
        deja_attache = self._session.execute(
            select(AppelOffreReferentielModele).where(
                AppelOffreReferentielModele.appel_offre_id == appel_offre_id,
                AppelOffreReferentielModele.referentiel_id == referentiel_id,
            )
        ).scalars().first()
        if deja_attache is not None:
            return
        self._session.add(
            AppelOffreReferentielModele(appel_offre_id=appel_offre_id, referentiel_id=referentiel_id)
        )
        self._session.commit()

    def detacher(self, appel_offre_id: UUID, referentiel_id: UUID) -> None:
        rattachement = self._session.execute(
            select(AppelOffreReferentielModele).where(
                AppelOffreReferentielModele.appel_offre_id == appel_offre_id,
                AppelOffreReferentielModele.referentiel_id == referentiel_id,
            )
        ).scalars().first()
        if rattachement is None:
            return
        self._session.delete(rattachement)
        self._session.commit()

    def lister_referentiels_pour_ao(self, appel_offre_id: UUID) -> list[Referentiel]:
        requete = (
            select(ReferentielModele)
            .join(
                AppelOffreReferentielModele,
                AppelOffreReferentielModele.referentiel_id == ReferentielModele.id,
            )
            .where(AppelOffreReferentielModele.appel_offre_id == appel_offre_id)
            .order_by(ReferentielModele.nom)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [referentiel_vers_entite(modele) for modele in modeles]

    def compter_ao_par_referentiel(self) -> dict[UUID, int]:
        requete = select(
            AppelOffreReferentielModele.referentiel_id,
            func.count(func.distinct(AppelOffreReferentielModele.appel_offre_id)),
        ).group_by(AppelOffreReferentielModele.referentiel_id)
        resultats = self._session.execute(requete).all()
        return {referentiel_id: nombre for referentiel_id, nombre in resultats}

    def compter_questions_actives_par_ao(self) -> dict[UUID, int]:
        requete = (
            select(AppelOffreReferentielModele.appel_offre_id, func.count(QuestionReferentielModele.id))
            .join(
                SectionReferentielModele,
                SectionReferentielModele.referentiel_id == AppelOffreReferentielModele.referentiel_id,
            )
            .join(
                QuestionReferentielModele,
                QuestionReferentielModele.section_id == SectionReferentielModele.id,
            )
            .where(QuestionReferentielModele.actif.is_(True))
            .group_by(AppelOffreReferentielModele.appel_offre_id)
        )
        resultats = self._session.execute(requete).all()
        return {appel_offre_id: nombre for appel_offre_id, nombre in resultats}
