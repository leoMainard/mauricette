"""Schémas Pydantic (contrats HTTP) pour le suivi du pipeline RAG des documents."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag
from mauricette.domaine.entites.enums import StatutEtape, StatutTache
from mauricette.domaine.entites.tache_traitement import TacheTraitement


class EtapeTraitementReponse(BaseModel):
    """Représentation HTTP d'une étape du pipeline RAG (extraction, découpage ou embedding)."""

    statut: StatutEtape
    message_erreur: str | None
    date_maj: datetime | None


class DocumentTraitementRagReponse(BaseModel):
    """Représentation HTTP du suivi de traitement RAG d'un document."""

    document_id: UUID
    extraction: EtapeTraitementReponse
    decoupage: EtapeTraitementReponse
    embedding: EtapeTraitementReponse
    statut_global: StatutEtape

    @classmethod
    def depuis_entite(cls, entite: DocumentTraitementRag) -> "DocumentTraitementRagReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            document_id=entite.document_id,
            extraction=EtapeTraitementReponse(
                statut=entite.extraction_statut,
                message_erreur=entite.extraction_message_erreur,
                date_maj=entite.extraction_date_maj,
            ),
            decoupage=EtapeTraitementReponse(
                statut=entite.decoupage_statut,
                message_erreur=entite.decoupage_message_erreur,
                date_maj=entite.decoupage_date_maj,
            ),
            embedding=EtapeTraitementReponse(
                statut=entite.embedding_statut,
                message_erreur=entite.embedding_message_erreur,
                date_maj=entite.embedding_date_maj,
            ),
            statut_global=entite.statut_global,
        )


class EtatAnalyseReponse(BaseModel):
    """Représentation HTTP de l'état de la dernière analyse (régénération) d'un AO."""

    statut: StatutTache
    message_erreur: str | None
    tentatives: int

    @classmethod
    def depuis_entite(cls, entite: TacheTraitement) -> "EtatAnalyseReponse":
        return cls(statut=entite.statut, message_erreur=entite.message_erreur, tentatives=entite.tentatives)
