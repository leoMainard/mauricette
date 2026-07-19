"""Modèles ORM SQLAlchemy (schéma de persistance PostgreSQL).

Ces classes ne sont PAS les entités du domaine : elles décrivent uniquement le
mapping objet-relationnel. La conversion entre modèle ORM et entité métier se
fait dans `mappers.py`, afin que le domaine reste totalement ignorant de
SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
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
    nom_original: Mapped[str] = mapped_column(String(500), nullable=False)
    cle_stockage: Mapped[str] = mapped_column(String(1000), nullable=False)
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
