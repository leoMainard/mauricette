"""Cas d'usage : dépôt d'un document dans un Appel d'Offres."""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID, uuid4

from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import StatutAppelOffre, TypeTache
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurDepotDocument
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.document_traitement_rag_repository import (
    DocumentTraitementRagRepositoryPort,
)
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort


@dataclass(frozen=True)
class CommandeDeposerDocument:
    """Données nécessaires au dépôt d'un document."""

    appel_offre_id: UUID
    nom_original: str
    contenu: BinaryIO
    type_mime: str


class DeposerDocument:
    """Orchestre le dépôt d'un document : écriture dans le stockage puis en base.

    Le fichier est d'abord écrit dans le stockage (local ou S3/MinIO selon la
    configuration), puis référencé en base via le repository. En cas d'échec de
    l'écriture, le document est tout de même journalisé avec le statut "en erreur".
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        depot_traitement_rag: DocumentTraitementRagRepositoryPort,
        depot_taches: TacheTraitementRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents
        self._depot_traitement_rag = depot_traitement_rag
        self._depot_taches = depot_taches
        self._stockage = stockage

    def executer(self, commande: CommandeDeposerDocument) -> Document:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        contenu_brut = commande.contenu.read()
        document_id = uuid4()
        cle_stockage = self._construire_cle_stockage(
            commande.appel_offre_id, document_id, commande.nom_original
        )

        document = Document(
            id=document_id,
            appel_offre_id=commande.appel_offre_id,
            nom_original=commande.nom_original,
            cle_stockage=cle_stockage,
            fournisseur_stockage=self._stockage.fournisseur,
            type_mime=commande.type_mime,
            taille_octets=len(contenu_brut),
            hash_sha256=hashlib.sha256(contenu_brut).hexdigest(),
        )

        try:
            self._stockage.enregistrer(cle_stockage, io.BytesIO(contenu_brut), commande.type_mime)
            document.marquer_televerse()
        except Exception as erreur:
            document.marquer_en_erreur()
            self._depot_documents.ajouter(document)
            raise ErreurDepotDocument(
                f"Échec du dépôt du document '{commande.nom_original}'"
            ) from erreur

        self._depot_documents.ajouter(document)
        self._depot_traitement_rag.creer(document.id, document.appel_offre_id)
        self._depot_taches.enqueuer(TypeTache.EXTRACTION_DOCUMENT, document.id)

        if appel_offre.statut == StatutAppelOffre.BROUILLON:
            appel_offre.passer_en_cours()
            self._depot_appels_offre.mettre_a_jour(appel_offre)

        return document

    @staticmethod
    def _construire_cle_stockage(appel_offre_id: UUID, document_id: UUID, nom_original: str) -> str:
        """Construit une clé de stockage unique, organisée par Appel d'Offres.

        `document_id` a son propre segment de chemin : `nom_original` peut contenir
        des "/" (arborescence d'un zip) sans ambiguïté avec le reste de la clé.
        """
        return f"appels_offre/{appel_offre_id}/{document_id}/{nom_original}"
