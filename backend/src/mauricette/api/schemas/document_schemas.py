"""Schémas Pydantic (contrats HTTP) pour les documents."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mauricette.application.cas_usage.deposer_fichier import ResultatDepotFichier
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import StatutDocument


class DocumentReponse(BaseModel):
    """Représentation HTTP d'un document (la clé de stockage interne n'est pas exposée)."""

    id: UUID
    appel_offre_id: UUID
    nom_original: str
    type_mime: str
    taille_octets: int
    statut: StatutDocument
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, document: Document) -> "DocumentReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=document.id,
            appel_offre_id=document.appel_offre_id,
            nom_original=document.nom_original,
            type_mime=document.type_mime,
            taille_octets=document.taille_octets,
            statut=document.statut,
            date_creation=document.date_creation,
            date_maj=document.date_maj,
        )


class DepotFichierReponse(BaseModel):
    """Bilan HTTP du dépôt d'un fichier : documents créés et doublons ignorés.

    Un seul fichier envoyé peut donner lieu à plusieurs documents créés (cas
    d'une archive zip éclatée), ou à aucun (fichier entièrement en doublon).
    """

    documents_crees: list[DocumentReponse]
    doublons_ignores: list[str]

    @classmethod
    def depuis_resultat(cls, resultat: ResultatDepotFichier) -> "DepotFichierReponse":
        """Construit le schéma de réponse à partir du DTO d'application `ResultatDepotFichier`."""
        return cls(
            documents_crees=[
                DocumentReponse.depuis_entite(document) for document in resultat.documents_crees
            ],
            doublons_ignores=resultat.doublons_ignores,
        )
