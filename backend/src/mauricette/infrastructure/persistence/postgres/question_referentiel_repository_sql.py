"""Adaptateur PostgreSQL du port `QuestionReferentielRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import (
    question_referentiel_vers_entite,
    question_referentiel_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import (
    QuestionReferentielModele,
    SectionReferentielModele,
)


class QuestionReferentielRepositorySQL(QuestionReferentielRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des questions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, question: QuestionReferentiel) -> None:
        self._session.add(question_referentiel_vers_modele(question))
        self._session.commit()

    def obtenir_par_id(self, question_id: UUID) -> QuestionReferentiel | None:
        modele = self._session.get(QuestionReferentielModele, question_id)
        return question_referentiel_vers_entite(modele) if modele else None

    def lister_par_section(self, section_id: UUID) -> list[QuestionReferentiel]:
        requete = (
            select(QuestionReferentielModele)
            .where(QuestionReferentielModele.section_id == section_id)
            .order_by(QuestionReferentielModele.ordre, QuestionReferentielModele.date_creation)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [question_referentiel_vers_entite(modele) for modele in modeles]

    def lister_par_referentiel(self, referentiel_id: UUID) -> list[QuestionReferentiel]:
        requete = (
            select(QuestionReferentielModele)
            .join(SectionReferentielModele, QuestionReferentielModele.section_id == SectionReferentielModele.id)
            .where(SectionReferentielModele.referentiel_id == referentiel_id)
            .order_by(SectionReferentielModele.ordre, QuestionReferentielModele.ordre)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [question_referentiel_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, question: QuestionReferentiel) -> None:
        modele = self._session.get(QuestionReferentielModele, question.id)
        if modele is None:
            raise ValueError(f"Question introuvable : {question.id}")
        modele.question = question.question
        modele.format_reponse = question.format_reponse.value
        modele.aide_extraction = question.aide_extraction
        modele.obligatoire = question.obligatoire
        modele.actif = question.actif
        modele.ordre = question.ordre
        modele.date_maj = question.date_maj
        self._session.commit()

    def supprimer(self, question_id: UUID) -> None:
        modele = self._session.get(QuestionReferentielModele, question_id)
        if modele is None:
            raise ValueError(f"Question introuvable : {question_id}")
        self._session.delete(modele)
        self._session.commit()

    def compter_actives_par_referentiel(self) -> dict[UUID, int]:
        requete = (
            select(SectionReferentielModele.referentiel_id, func.count(QuestionReferentielModele.id))
            .join(
                QuestionReferentielModele,
                QuestionReferentielModele.section_id == SectionReferentielModele.id,
            )
            .where(QuestionReferentielModele.actif.is_(True))
            .group_by(SectionReferentielModele.referentiel_id)
        )
        resultats = self._session.execute(requete).all()
        return {referentiel_id: nombre for referentiel_id, nombre in resultats}
