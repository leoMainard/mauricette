"""Adaptateur PostgreSQL du port `ReponseQuestionRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import case, delete, func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.reponse_question import ReponseQuestion
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    reponse_question_vers_entite,
    reponse_question_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import (
    QuestionReferentielModele,
    ReponseQuestionModele,
    SectionReferentielModele,
)


class ReponseQuestionRepositorySQL(ReponseQuestionRepositoryPort):
    """Implémentation PostgreSQL du repository des réponses générées."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def remplacer_pour_appel_offre(self, appel_offre_id: UUID, reponses: list[ReponseQuestion]) -> None:
        self._session.execute(
            delete(ReponseQuestionModele).where(ReponseQuestionModele.appel_offre_id == appel_offre_id)
        )
        for reponse in reponses:
            self._session.add(reponse_question_vers_modele(reponse))
        self._session.commit()

    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[ReponseQuestion]:
        requete = select(ReponseQuestionModele).where(
            ReponseQuestionModele.appel_offre_id == appel_offre_id
        )
        modeles = self._session.execute(requete).scalars().all()
        return [reponse_question_vers_entite(modele) for modele in modeles]

    def obtenir_par_appel_offre_et_question(
        self, appel_offre_id: UUID, question_referentiel_id: UUID
    ) -> ReponseQuestion | None:
        requete = select(ReponseQuestionModele).where(
            ReponseQuestionModele.appel_offre_id == appel_offre_id,
            ReponseQuestionModele.question_referentiel_id == question_referentiel_id,
        )
        modele = self._session.execute(requete).scalar_one_or_none()
        return reponse_question_vers_entite(modele) if modele else None

    def obtenir_par_id(self, reponse_id: UUID) -> ReponseQuestion | None:
        modele = self._session.get(ReponseQuestionModele, reponse_id)
        return reponse_question_vers_entite(modele) if modele else None

    def mettre_a_jour(self, reponse: ReponseQuestion) -> None:
        modele = self._session.get(ReponseQuestionModele, reponse.id)
        if modele is None:
            raise ValueError(f"Réponse introuvable : {reponse.id}")
        modele.statut = reponse.statut.value
        modele.date_maj = reponse.date_maj
        self._session.commit()

    def compter_avec_contenu_par_appel_offre(self) -> dict[UUID, int]:
        requete = (
            select(ReponseQuestionModele.appel_offre_id, func.count(ReponseQuestionModele.id))
            .where(ReponseQuestionModele.contenu.is_not(None))
            .group_by(ReponseQuestionModele.appel_offre_id)
        )
        resultats = self._session.execute(requete).all()
        return {appel_offre_id: nombre for appel_offre_id, nombre in resultats}

    def compter_total(self) -> int:
        requete = select(func.count(ReponseQuestionModele.id))
        return self._session.execute(requete).scalar_one()

    def compter_par_statut(self) -> dict[str, int]:
        requete = select(ReponseQuestionModele.statut, func.count(ReponseQuestionModele.id)).group_by(
            ReponseQuestionModele.statut
        )
        return dict(self._session.execute(requete).all())

    def lister_scores_confiance(self) -> list[float]:
        requete = select(ReponseQuestionModele.score_confiance).where(
            ReponseQuestionModele.score_confiance.is_not(None)
        )
        return list(self._session.execute(requete).scalars().all())

    def compter_sans_contenu_par_referentiel(self) -> dict[UUID, dict[str, int]]:
        requete = (
            select(
                SectionReferentielModele.referentiel_id,
                func.sum(case((ReponseQuestionModele.contenu.is_not(None), 1), else_=0)),
                func.sum(case((ReponseQuestionModele.contenu.is_(None), 1), else_=0)),
            )
            .join(
                QuestionReferentielModele,
                QuestionReferentielModele.id == ReponseQuestionModele.question_referentiel_id,
            )
            .join(
                SectionReferentielModele,
                SectionReferentielModele.id == QuestionReferentielModele.section_id,
            )
            .group_by(SectionReferentielModele.referentiel_id)
        )
        resultat: dict[UUID, dict[str, int]] = {}
        for referentiel_id, avec, sans in self._session.execute(requete).all():
            resultat[referentiel_id] = {"avec": int(avec), "sans": int(sans)}
        return resultat
