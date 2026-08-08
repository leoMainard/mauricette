"""Adaptateur PostgreSQL du port `FeedbackReponseRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback
from mauricette.domaine.entites.feedback_reponse import FeedbackReponse
from mauricette.domaine.ports.feedback_reponse_repository import (
    FeedbackReponseDetaille,
    FeedbackReponseRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import (
    feedback_reponse_vers_entite,
    feedback_reponse_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import (
    AppelOffreModele,
    FeedbackReponseModele,
    QuestionReferentielModele,
    ReferentielModele,
    SectionReferentielModele,
)


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

    def compter_par_avis(self) -> dict[str, int]:
        requete = (
            select(FeedbackReponseModele.avis, func.count(FeedbackReponseModele.id))
            .where(FeedbackReponseModele.avis.is_not(None))
            .group_by(FeedbackReponseModele.avis)
        )
        resultats = self._session.execute(requete).all()
        return {avis: nombre for avis, nombre in resultats}

    def compter_par_type_erreur(self) -> dict[str, int]:
        requete = (
            select(FeedbackReponseModele.type_erreur, func.count(FeedbackReponseModele.id))
            .where(FeedbackReponseModele.type_erreur.is_not(None))
            .group_by(FeedbackReponseModele.type_erreur)
        )
        resultats = self._session.execute(requete).all()
        return {type_erreur: nombre for type_erreur, nombre in resultats}

    def compter_negatifs_par_referentiel(self) -> dict[UUID, int]:
        requete = (
            select(
                SectionReferentielModele.referentiel_id,
                func.count(FeedbackReponseModele.id),
            )
            .join(
                QuestionReferentielModele,
                QuestionReferentielModele.id == FeedbackReponseModele.question_referentiel_id,
            )
            .join(
                SectionReferentielModele,
                SectionReferentielModele.id == QuestionReferentielModele.section_id,
            )
            .where(FeedbackReponseModele.avis == Avis.NEGATIF.value)
            .group_by(SectionReferentielModele.referentiel_id)
        )
        resultats = self._session.execute(requete).all()
        return {referentiel_id: nombre for referentiel_id, nombre in resultats}

    def lister_tous_avec_contexte(self) -> list[FeedbackReponseDetaille]:
        requete = (
            select(
                FeedbackReponseModele,
                AppelOffreModele.nom,
                ReferentielModele.id,
                ReferentielModele.nom,
                QuestionReferentielModele.question,
            )
            .join(AppelOffreModele, AppelOffreModele.id == FeedbackReponseModele.appel_offre_id)
            .join(
                QuestionReferentielModele,
                QuestionReferentielModele.id == FeedbackReponseModele.question_referentiel_id,
            )
            .join(
                SectionReferentielModele,
                SectionReferentielModele.id == QuestionReferentielModele.section_id,
            )
            .join(ReferentielModele, ReferentielModele.id == SectionReferentielModele.referentiel_id)
        )
        resultats = self._session.execute(requete).all()
        return [
            FeedbackReponseDetaille(
                id=feedback.id,
                appel_offre_id=feedback.appel_offre_id,
                appel_offre_nom=appel_offre_nom,
                referentiel_id=referentiel_id,
                referentiel_nom=referentiel_nom,
                question_referentiel_id=feedback.question_referentiel_id,
                question=question,
                avis=Avis(feedback.avis) if feedback.avis else None,
                commentaire=feedback.commentaire,
                contenu_reponse_snapshot=feedback.contenu_reponse_snapshot,
                source_attendue=feedback.source_attendue,
                citation_attendue=feedback.citation_attendue,
                type_erreur=TypeErreurFeedback(feedback.type_erreur) if feedback.type_erreur else None,
                details_erreur=feedback.details_erreur,
                date_creation=feedback.date_creation,
            )
            for feedback, appel_offre_nom, referentiel_id, referentiel_nom, question in resultats
        ]
