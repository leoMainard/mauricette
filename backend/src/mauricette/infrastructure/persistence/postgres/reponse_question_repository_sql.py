"""Adaptateur PostgreSQL du port `ReponseQuestionRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.reponse_question import ReponseQuestion
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    reponse_question_vers_entite,
    reponse_question_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import ReponseQuestionModele


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
