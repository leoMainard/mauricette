"""Adaptateur PostgreSQL du port `DocumentTraitementRagRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.document_traitement_rag import DocumentTraitementRag
from mauricette.domaine.entites.enums import StatutEtape
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import (
    document_traitement_rag_vers_entite,
    document_traitement_rag_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import DocumentTraitementRagModele


class DocumentTraitementRagRepositorySQL(DocumentTraitementRagRepositoryPort):
    """Implémentation PostgreSQL du suivi de traitement RAG des documents."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def creer(self, document_id: UUID, appel_offre_id: UUID) -> DocumentTraitementRag:
        entite = DocumentTraitementRag(document_id=document_id, appel_offre_id=appel_offre_id)
        self._session.add(document_traitement_rag_vers_modele(entite))
        self._session.commit()
        return entite

    def obtenir(self, document_id: UUID) -> DocumentTraitementRag | None:
        modele = self._session.get(DocumentTraitementRagModele, document_id)
        return document_traitement_rag_vers_entite(modele) if modele else None

    def mettre_a_jour(self, entite: DocumentTraitementRag) -> None:
        modele = self._session.get(DocumentTraitementRagModele, entite.document_id)
        if modele is None:
            raise ValueError(f"Suivi de traitement RAG introuvable pour le document : {entite.document_id}")
        modele.extraction_statut = entite.extraction_statut.value
        modele.extraction_message_erreur = entite.extraction_message_erreur
        modele.extraction_date_maj = entite.extraction_date_maj
        modele.decoupage_statut = entite.decoupage_statut.value
        modele.decoupage_message_erreur = entite.decoupage_message_erreur
        modele.decoupage_date_maj = entite.decoupage_date_maj
        modele.embedding_statut = entite.embedding_statut.value
        modele.embedding_message_erreur = entite.embedding_message_erreur
        modele.embedding_date_maj = entite.embedding_date_maj
        modele.date_maj = entite.date_maj
        self._session.commit()

    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[DocumentTraitementRag]:
        requete = select(DocumentTraitementRagModele).where(
            DocumentTraitementRagModele.appel_offre_id == appel_offre_id
        )
        modeles = self._session.execute(requete).scalars().all()
        return [document_traitement_rag_vers_entite(modele) for modele in modeles]

    def compter_par_etape_et_statut(self) -> dict[str, dict[str, int]]:
        colonnes_par_etape = {
            "extraction": DocumentTraitementRagModele.extraction_statut,
            "decoupage": DocumentTraitementRagModele.decoupage_statut,
            "embedding": DocumentTraitementRagModele.embedding_statut,
        }
        resultat: dict[str, dict[str, int]] = {}
        for etape, colonne in colonnes_par_etape.items():
            requete = select(colonne, func.count(DocumentTraitementRagModele.document_id)).group_by(colonne)
            resultat[etape] = dict(self._session.execute(requete).all())
        return resultat

    def duree_moyenne_traitement_secondes(self) -> float | None:
        requete = select(
            func.avg(
                func.extract(
                    "epoch",
                    DocumentTraitementRagModele.embedding_date_maj - DocumentTraitementRagModele.date_creation,
                )
            )
        ).where(DocumentTraitementRagModele.embedding_statut == StatutEtape.REUSSI.value)
        resultat = self._session.execute(requete).scalar_one_or_none()
        return float(resultat) if resultat is not None else None
