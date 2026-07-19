"""Schémas Pydantic (contrats HTTP) exposés par l'API."""

from mauricette.api.schemas.appel_offre_schemas import (
    AppelOffreAvecStatistiquesReponse,
    AppelOffreDetailReponse,
    AppelOffreReponse,
    CreationAppelOffreRequete,
    ModificationAppelOffreRequete,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse, DocumentReponse
from mauricette.api.schemas.referentiel_schemas import (
    ContenuQuestionReferentielRequete,
    CreationReferentielRequete,
    CreationSectionRequete,
    DetailReferentielReponse,
    ModificationActivationQuestionRequete,
    ModificationReferentielRequete,
    ModificationSectionRequete,
    QuestionReferentielReponse,
    RattachementReferentielRequete,
    ReferentielAvecStatistiquesReponse,
    ReferentielReponse,
    SectionAvecQuestionsReponse,
    SectionReponse,
)

__all__ = [
    "AppelOffreAvecStatistiquesReponse",
    "AppelOffreDetailReponse",
    "AppelOffreReponse",
    "ContenuQuestionReferentielRequete",
    "CreationAppelOffreRequete",
    "CreationReferentielRequete",
    "CreationSectionRequete",
    "DepotFichierReponse",
    "DetailReferentielReponse",
    "DocumentReponse",
    "ModificationActivationQuestionRequete",
    "ModificationAppelOffreRequete",
    "ModificationReferentielRequete",
    "ModificationSectionRequete",
    "QuestionReferentielReponse",
    "RattachementReferentielRequete",
    "ReferentielAvecStatistiquesReponse",
    "ReferentielReponse",
    "SectionAvecQuestionsReponse",
    "SectionReponse",
]
