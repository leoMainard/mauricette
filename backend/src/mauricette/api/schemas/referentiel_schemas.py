"""Schémas Pydantic (contrats HTTP) pour les référentiels, sections et questions."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mauricette.application.cas_usage.lister_referentiels import ReferentielAvecStatistiques
from mauricette.application.cas_usage.obtenir_referentiel_detail import (
    DetailReferentiel,
    SectionAvecQuestions,
)
from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.entites.section_referentiel import SectionReferentiel

# --- Référentiel ---


class CreationReferentielRequete(BaseModel):
    """Corps de requête pour la création d'un référentiel."""

    nom: str = Field(min_length=1, max_length=255)
    description: str | None = None
    actif_par_defaut: bool = False


class ModificationReferentielRequete(BaseModel):
    """Corps de requête pour la modification d'un référentiel."""

    nom: str = Field(min_length=1, max_length=255)
    description: str | None = None
    actif_par_defaut: bool = False


class ReferentielReponse(BaseModel):
    """Représentation HTTP d'un référentiel."""

    id: UUID
    nom: str
    description: str | None
    actif_par_defaut: bool
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: Referentiel) -> "ReferentielReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            nom=entite.nom,
            description=entite.description,
            actif_par_defaut=entite.actif_par_defaut,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )


class ReferentielAvecStatistiquesReponse(BaseModel):
    """Représentation HTTP d'un référentiel enrichi de ses statistiques."""

    referentiel: ReferentielReponse
    nombre_sections: int
    nombre_questions_actives: int
    nombre_ao_concernes: int

    @classmethod
    def depuis_dto(cls, dto: ReferentielAvecStatistiques) -> "ReferentielAvecStatistiquesReponse":
        """Construit le schéma de réponse à partir du DTO d'application."""
        return cls(
            referentiel=ReferentielReponse.depuis_entite(dto.referentiel),
            nombre_sections=dto.nombre_sections,
            nombre_questions_actives=dto.nombre_questions_actives,
            nombre_ao_concernes=dto.nombre_ao_concernes,
        )


# --- Section ---


class CreationSectionRequete(BaseModel):
    """Corps de requête pour la création d'une section."""

    nom: str = Field(min_length=1, max_length=255)


class ModificationSectionRequete(BaseModel):
    """Corps de requête pour le renommage d'une section."""

    nom: str = Field(min_length=1, max_length=255)


class ReordonnerSectionsRequete(BaseModel):
    """Corps de requête pour réordonner les sections d'un référentiel."""

    ids_ordonnes: list[UUID]


class SectionReponse(BaseModel):
    """Représentation HTTP d'une section."""

    id: UUID
    referentiel_id: UUID
    nom: str
    ordre: int
    date_creation: datetime

    @classmethod
    def depuis_entite(cls, entite: SectionReferentiel) -> "SectionReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            referentiel_id=entite.referentiel_id,
            nom=entite.nom,
            ordre=entite.ordre,
            date_creation=entite.date_creation,
        )


# --- Question ---


class ContenuQuestionReferentielRequete(BaseModel):
    """Corps de requête commun à la création et à la modification d'une question."""

    question: str = Field(min_length=1, description="Intitulé de la question")
    format_reponse: FormatReponse
    aide_extraction: str | None = Field(
        default=None, description="Précise ce que le RAG doit chercher dans les documents"
    )
    obligatoire: bool = False


class ModificationActivationQuestionRequete(BaseModel):
    """Corps de requête pour archiver/réactiver une question."""

    actif: bool


class ReordonnerQuestionsRequete(BaseModel):
    """Corps de requête pour réordonner les questions d'une section."""

    ids_ordonnes: list[UUID]


class QuestionReferentielReponse(BaseModel):
    """Représentation HTTP d'une question de référentiel."""

    id: UUID
    section_id: UUID
    question: str
    format_reponse: FormatReponse
    aide_extraction: str | None
    obligatoire: bool
    actif: bool
    ordre: int
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: QuestionReferentiel) -> "QuestionReferentielReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            section_id=entite.section_id,
            question=entite.question,
            format_reponse=entite.format_reponse,
            aide_extraction=entite.aide_extraction,
            obligatoire=entite.obligatoire,
            actif=entite.actif,
            ordre=entite.ordre,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )


# --- Détail agrégé d'un référentiel ---


class SectionAvecQuestionsReponse(BaseModel):
    """Représentation HTTP d'une section accompagnée de ses questions."""

    section: SectionReponse
    questions: list[QuestionReferentielReponse]

    @classmethod
    def depuis_dto(cls, dto: SectionAvecQuestions) -> "SectionAvecQuestionsReponse":
        """Construit le schéma de réponse à partir du DTO d'application."""
        return cls(
            section=SectionReponse.depuis_entite(dto.section),
            questions=[QuestionReferentielReponse.depuis_entite(q) for q in dto.questions],
        )


class DetailReferentielReponse(BaseModel):
    """Représentation HTTP complète d'un référentiel : sections, questions, statistiques."""

    referentiel: ReferentielReponse
    sections: list[SectionAvecQuestionsReponse]
    nombre_ao_concernes: int

    @classmethod
    def depuis_dto(cls, dto: DetailReferentiel) -> "DetailReferentielReponse":
        """Construit le schéma de réponse à partir du DTO d'application."""
        return cls(
            referentiel=ReferentielReponse.depuis_entite(dto.referentiel),
            sections=[SectionAvecQuestionsReponse.depuis_dto(s) for s in dto.sections],
            nombre_ao_concernes=dto.nombre_ao_concernes,
        )


# --- Rattachement référentiel ↔ Appel d'Offres ---


class RattachementReferentielRequete(BaseModel):
    """Corps de requête pour rattacher un référentiel à un Appel d'Offres."""

    referentiel_id: UUID
