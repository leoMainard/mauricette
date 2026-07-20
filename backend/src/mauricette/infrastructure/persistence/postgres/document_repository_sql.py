"""Adaptateur PostgreSQL du port `DocumentRepositoryPort`."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import StatutDocument
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort, StatistiquesDocuments
from mauricette.infrastructure.persistence.postgres.mappers import (
    document_vers_entite,
    document_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import DocumentModele


class DocumentRepositorySQL(DocumentRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des documents."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, document: Document) -> None:
        self._session.add(document_vers_modele(document))
        self._session.commit()

    def obtenir_par_id(self, document_id: UUID) -> Document | None:
        modele = self._session.get(DocumentModele, document_id)
        return document_vers_entite(modele) if modele else None

    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[Document]:
        requete = (
            select(DocumentModele)
            .where(DocumentModele.appel_offre_id == appel_offre_id)
            .order_by(DocumentModele.date_creation)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [document_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, document: Document) -> None:
        modele = self._session.get(DocumentModele, document.id)
        if modele is None:
            raise ValueError(f"Document introuvable : {document.id}")
        modele.statut = document.statut.value
        modele.hash_sha256 = document.hash_sha256
        modele.date_maj = document.date_maj
        self._session.commit()

    def obtenir_par_hash(self, appel_offre_id: UUID, hash_sha256: str) -> Document | None:
        requete = select(DocumentModele).where(
            DocumentModele.appel_offre_id == appel_offre_id,
            DocumentModele.hash_sha256 == hash_sha256,
        )
        modele = self._session.execute(requete).scalars().first()
        return document_vers_entite(modele) if modele else None

    def supprimer(self, document_id: UUID) -> None:
        modele = self._session.get(DocumentModele, document_id)
        if modele is None:
            raise ValueError(f"Document introuvable : {document_id}")
        self._session.delete(modele)
        self._session.commit()

    def compter_par_appel_offre(self) -> dict[UUID, StatistiquesDocuments]:
        requete = select(
            DocumentModele.appel_offre_id,
            func.count(DocumentModele.id),
            func.coalesce(func.sum(DocumentModele.taille_octets), 0),
        ).group_by(DocumentModele.appel_offre_id)

        resultats = self._session.execute(requete).all()
        return {
            appel_offre_id: StatistiquesDocuments(
                nombre_documents=nombre, taille_totale_octets=int(taille_totale)
            )
            for appel_offre_id, nombre, taille_totale in resultats
        }

    def compter_traites_par_jour(self) -> dict[date, int]:
        jour = func.date_trunc("day", DocumentModele.date_maj)
        requete = (
            select(jour, func.count(DocumentModele.id))
            .where(DocumentModele.statut == StatutDocument.TRAITE.value)
            .group_by(jour)
        )
        resultats = self._session.execute(requete).all()
        return {debut_jour.date(): nombre for debut_jour, nombre in resultats}
