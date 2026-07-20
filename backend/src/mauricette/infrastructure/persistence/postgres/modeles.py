"""Modèles ORM SQLAlchemy (schéma de persistance PostgreSQL).

Ces classes ne sont PAS les entités du domaine : elles décrivent uniquement le
mapping objet-relationnel. La conversion entre modèle ORM et entité métier se
fait dans `mappers.py`, afin que le domaine reste totalement ignorant de
SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    Computed,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mauricette.infrastructure.persistence.postgres.base import Base

# Dimension des vecteurs produits par mistral-embed. Si le fournisseur d'embedding
# change un jour pour un modèle à dimension différente, cette constante (et la
# migration Alembic associée) devront être mises à jour en conséquence.
DIMENSION_EMBEDDING = 1024


class AppelOffreModele(Base):
    """Table `appel_offre`."""

    __tablename__ = "appel_offre"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    cree_par: Mapped[str] = mapped_column(String(255), nullable=False)
    statut: Mapped[str] = mapped_column(String(50), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    documents: Mapped[list["DocumentModele"]] = relationship(
        back_populates="appel_offre",
        cascade="all, delete-orphan",
        order_by="DocumentModele.date_creation",
    )


class DocumentModele(Base):
    """Table `document`."""

    __tablename__ = "document"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )
    # Longueurs généreuses : peut contenir le chemin relatif complet d'un zip
    # (ex: "Lot1/CCTP/cctp.pdf") pour en conserver l'arborescence.
    nom_original: Mapped[str] = mapped_column(String(2000), nullable=False)
    cle_stockage: Mapped[str] = mapped_column(String(2500), nullable=False)
    fournisseur_stockage: Mapped[str] = mapped_column(String(50), nullable=False)
    type_mime: Mapped[str] = mapped_column(String(255), nullable=False)
    taille_octets: Mapped[int] = mapped_column(BigInteger, nullable=False)
    hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    statut: Mapped[str] = mapped_column(String(50), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    appel_offre: Mapped[AppelOffreModele] = relationship(back_populates="documents")


class ReferentielModele(Base):
    """Table `referentiel`."""

    __tablename__ = "referentiel"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif_par_defaut: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[list["SectionReferentielModele"]] = relationship(
        back_populates="referentiel",
        cascade="all, delete-orphan",
        order_by="SectionReferentielModele.ordre",
    )


class SectionReferentielModele(Base):
    """Table `section_referentiel`."""

    __tablename__ = "section_referentiel"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    referentiel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("referentiel.id", ondelete="CASCADE"), nullable=False
    )
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    referentiel: Mapped[ReferentielModele] = relationship(back_populates="sections")
    questions: Mapped[list["QuestionReferentielModele"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="QuestionReferentielModele.ordre",
    )


class QuestionReferentielModele(Base):
    """Table `question_referentiel`."""

    __tablename__ = "question_referentiel"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    section_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("section_referentiel.id", ondelete="CASCADE"), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    format_reponse: Mapped[str] = mapped_column(String(50), nullable=False)
    aide_extraction: Mapped[str | None] = mapped_column(Text, nullable=True)
    obligatoire: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    section: Mapped[SectionReferentielModele] = relationship(back_populates="questions")


class AppelOffreReferentielModele(Base):
    """Table `appel_offre_referentiel` : rattachement d'un référentiel à un AO."""

    __tablename__ = "appel_offre_referentiel"
    __table_args__ = (UniqueConstraint("appel_offre_id", "referentiel_id"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )
    referentiel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("referentiel.id", ondelete="CASCADE"), nullable=False
    )
    date_ajout: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentTraitementRagModele(Base):
    """Table `document_traitement_rag` : suivi de l'avancement du pipeline RAG d'un document."""

    __tablename__ = "document_traitement_rag"

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("document.id", ondelete="CASCADE"), primary_key=True
    )
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )

    extraction_statut: Mapped[str] = mapped_column(String(20), nullable=False)
    extraction_message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_date_maj: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    decoupage_statut: Mapped[str] = mapped_column(String(20), nullable=False)
    decoupage_message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
    decoupage_date_maj: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    embedding_statut: Mapped[str] = mapped_column(String(20), nullable=False)
    embedding_message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_date_maj: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChunkModele(Base):
    """Table `chunk` : fragment de contenu d'un document, avec son vecteur d'embedding."""

    __tablename__ = "chunk"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("document.id", ondelete="CASCADE"), nullable=False
    )
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )
    contenu: Mapped[str] = mapped_column(Text, nullable=False)
    # Colonne générée par Postgres (voir migration), utilisée par la recherche
    # plein texte de `recherche_hybride` : jamais écrite depuis Python.
    contenu_tsv: Mapped[str] = mapped_column(
        TSVECTOR, Computed("to_tsvector('french', contenu)", persisted=True), nullable=True
    )
    type_chunk: Mapped[str] = mapped_column(String(20), nullable=False)
    page_debut: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_fin: Mapped[int | None] = mapped_column(Integer, nullable=True)
    titre_section: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(DIMENSION_EMBEDDING), nullable=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TacheTraitementModele(Base):
    """Table `tache_traitement` : file d'attente des traitements RAG asynchrones.

    `reference_id` est une cible polymorphe (pas de clé étrangère) : selon
    `type_tache`, il désigne l'identifiant du document à traiter.
    """

    __tablename__ = "tache_traitement"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    type_tache: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False)
    tentatives: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_prochaine_tentative: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_reservation: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ReponseQuestionModele(Base):
    """Table `reponse_question` : réponse générée par le RAG pour une question, sur un AO."""

    __tablename__ = "reponse_question"
    __table_args__ = (UniqueConstraint("appel_offre_id", "question_referentiel_id"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )
    question_referentiel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("question_referentiel.id", ondelete="CASCADE"), nullable=False
    )
    contenu: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_confiance: Mapped[float | None] = mapped_column(Float, nullable=True)
    statut: Mapped[str] = mapped_column(String(30), nullable=False)
    citations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_maj: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MessageChatbotModele(Base):
    """Table `message_chatbot` : fil de discussion du chatbot d'un AO (question et réponses)."""

    __tablename__ = "message_chatbot"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    appel_offre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("appel_offre.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    contenu: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_confiance: Mapped[float | None] = mapped_column(Float, nullable=True)
    citations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
