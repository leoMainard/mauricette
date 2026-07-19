"""Ports (interfaces) du domaine, à implémenter par la couche infrastructure."""

from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)
from mauricette.domaine.ports.stockage_document import StockageDocumentPort

__all__ = [
    "AppelOffreRepositoryPort",
    "DocumentRepositoryPort",
    "QuestionReferentielRepositoryPort",
    "ReferentielAppelOffreRepositoryPort",
    "ReferentielRepositoryPort",
    "SectionReferentielRepositoryPort",
    "StockageDocumentPort",
]
