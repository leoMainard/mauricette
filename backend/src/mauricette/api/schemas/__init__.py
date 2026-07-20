"""Schémas Pydantic (contrats HTTP) exposés par l'API."""

from mauricette.api.schemas.appel_offre_schemas import (
    AppelOffreAvecStatistiquesReponse,
    AppelOffreDetailReponse,
    AppelOffreReponse,
    CreationAppelOffreRequete,
    ModificationAppelOffreRequete,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse, DocumentReponse
from mauricette.api.schemas.reponse_question_schemas import CitationReponse, ReponseQuestionReponse
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
from mauricette.api.schemas.traitement_rag_schemas import (
    DocumentTraitementRagReponse,
    EtapeTraitementReponse,
)

__all__ = [
    "AppelOffreAvecStatistiquesReponse",
    "AppelOffreDetailReponse",
    "AppelOffreReponse",
    "CitationReponse",
    "ContenuQuestionReferentielRequete",
    "CreationAppelOffreRequete",
    "CreationReferentielRequete",
    "CreationSectionRequete",
    "DepotFichierReponse",
    "DetailReferentielReponse",
    "DocumentReponse",
    "DocumentTraitementRagReponse",
    "EtapeTraitementReponse",
    "ModificationActivationQuestionRequete",
    "ModificationAppelOffreRequete",
    "ModificationReferentielRequete",
    "ModificationSectionRequete",
    "QuestionReferentielReponse",
    "RattachementReferentielRequete",
    "ReferentielAvecStatistiquesReponse",
    "ReferentielReponse",
    "ReponseQuestionReponse",
    "SectionAvecQuestionsReponse",
    "SectionReponse",
]
