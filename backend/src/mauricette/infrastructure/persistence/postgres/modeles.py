"""Modèles ORM SQLAlchemy (schéma de persistance PostgreSQL).

Ces classes ne sont PAS les entités du domaine : elles décrivent uniquement le
mapping objet-relationnel. La conversion entre modèle ORM et entité métier se
fait dans `mappers.py`, afin que le domaine reste totalement ignorant de
SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mauricette.infrastructure.persistence.postgres.base import Base


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
