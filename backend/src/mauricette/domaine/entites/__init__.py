"""Entités métier de Mauricette (aucune dépendance vers l'infrastructure)."""

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.chunk import Chunk
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag
from mauricette.domaine.entites.enums import (
    FormatReponse,
    FournisseurStockage,
    StatutAppelOffre,
    StatutDocument,
    StatutEtape,
    StatutReponse,
    StatutTache,
    TypeChunk,
    TypeTache,
)
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.entites.reponse_question import Citation, ReponseQuestion
from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.entites.tache_traitement import TacheTraitement

__all__ = [
    "AppelOffre",
    "Chunk",
    "Citation",
    "Document",
    "DocumentTraitementRag",
    "FormatReponse",
    "FournisseurStockage",
    "QuestionReferentiel",
    "Referentiel",
    "ReponseQuestion",
    "SectionReferentiel",
    "StatutAppelOffre",
    "StatutDocument",
    "StatutEtape",
    "StatutReponse",
    "StatutTache",
    "TacheTraitement",
    "TypeChunk",
    "TypeTache",
]
