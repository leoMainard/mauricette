"""Adaptateur PostgreSQL du port `FeedbackReponseRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.feedback_reponse import FeedbackReponse
from mauricette.domaine.ports.feedback_reponse_repository import FeedbackReponseRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    feedback_reponse_vers_entite,
    feedback_reponse_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import FeedbackReponseModele


class FeedbackReponseRepositorySQL(FeedbackReponseRepositoryPort):
    """Implémentation PostgreSQL du repository du feedback par réponse."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def enregistrer(self, feedback: FeedbackReponse) -> FeedbackReponse:
        modele_existant = self._session.execute(
            select(FeedbackReponseModele).where(
                FeedbackReponseModele.appel_offre_id == feedback.appel_offre_id,
                FeedbackReponseModele.question_referentiel_id == feedback.question_referentiel_id,
            )
        ).scalar_one_or_none()

        if modele_existant is None:
            modele = feedback_reponse_vers_modele(feedback)
            self._session.add(modele)
        else:
            modele_existant.avis = feedback.avis.value if feedback.avis else None
            modele_existant.contenu_reponse_snapshot = feedback.contenu_reponse_snapshot
            modele_existant.commentaire = feedback.commentaire
            modele_existant.source_attendue = feedback.source_attendue
            modele_existant.citation_attendue = feedback.citation_attendue
            modele_existant.type_erreur = feedback.type_erreur.value if feedback.type_erreur else None
            modele_existant.details_erreur = feedback.details_erreur
            modele = modele_existant

        self._session.commit()
        return feedback_reponse_vers_entite(modele)

    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[FeedbackReponse]:
        requete = select(FeedbackReponseModele).where(
            FeedbackReponseModele.appel_offre_id == appel_offre_id
        )
        modeles = self._session.execute(requete).scalars().all()
        return [feedback_reponse_vers_entite(modele) for modele in modeles]
