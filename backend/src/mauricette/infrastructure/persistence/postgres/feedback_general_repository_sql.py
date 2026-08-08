"""Adaptateur PostgreSQL du port `FeedbackGeneralRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.ports.feedback_general_repository import FeedbackGeneralRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    feedback_general_vers_entite,
    feedback_general_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import FeedbackGeneralModele


class FeedbackGeneralRepositorySQL(FeedbackGeneralRepositoryPort):
    """Implémentation PostgreSQL du repository du feedback général."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def enregistrer(self, feedback: FeedbackGeneral) -> FeedbackGeneral:
        modele_existant = self._session.execute(
            select(FeedbackGeneralModele).where(
                FeedbackGeneralModele.appel_offre_id == feedback.appel_offre_id
            )
        ).scalar_one_or_none()

        if modele_existant is None:
            modele = feedback_general_vers_modele(feedback)
            self._session.add(modele)
        else:
            modele_existant.avis = feedback.avis.value if feedback.avis else None
            modele_existant.commentaire = feedback.commentaire
            modele = modele_existant

        self._session.commit()
        return feedback_general_vers_entite(modele)

    def obtenir_par_appel_offre(self, appel_offre_id: UUID) -> FeedbackGeneral | None:
        modele = self._session.execute(
            select(FeedbackGeneralModele).where(FeedbackGeneralModele.appel_offre_id == appel_offre_id)
        ).scalar_one_or_none()
        return feedback_general_vers_entite(modele) if modele else None

    def compter_par_avis(self) -> dict[str, int]:
        requete = (
            select(FeedbackGeneralModele.avis, func.count(FeedbackGeneralModele.id))
            .where(FeedbackGeneralModele.avis.is_not(None))
            .group_by(FeedbackGeneralModele.avis)
        )
        resultats = self._session.execute(requete).all()
        return {avis: nombre for avis, nombre in resultats}

    def lister_tous(self) -> list[FeedbackGeneral]:
        modeles = self._session.execute(select(FeedbackGeneralModele)).scalars().all()
        return [feedback_general_vers_entite(modele) for modele in modeles]
