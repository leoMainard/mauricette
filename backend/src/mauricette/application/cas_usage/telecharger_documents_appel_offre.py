"""Cas d'usage : téléchargement groupé (ZIP) de tous les documents d'un Appel d'Offres."""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


@dataclass(frozen=True)
class ContenuZip:
    """Octets bruts d'une archive ZIP, avec le nom de l'AO pour nommer le fichier téléchargé."""

    contenu: bytes
    nom_appel_offre: str


class TelechargerDocumentsAppelOffre:
    """Regroupe tous les documents d'un Appel d'Offres dans une archive ZIP en mémoire."""

    def __init__(
        self,
        depot_documents: DocumentRepositoryPort,
        depot_appels_offre: AppelOffreRepositoryPort,
        stockage: StockageDocumentPort,
    ) -> None:
        self._depot_documents = depot_documents
        self._depot_appels_offre = depot_appels_offre
        self._stockage = stockage

    def executer(self, appel_offre_id: UUID) -> ContenuZip:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'offres introuvable : {appel_offre_id}")

        documents = self._depot_documents.lister_par_appel_offre(appel_offre_id)
        tampon = io.BytesIO()
        with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as zip_fichier:
            for document in documents:
                # Un document à la fois : évite de charger tous les contenus en mémoire
                # simultanément avant de les écrire dans l'archive.
                contenu = self._stockage.recuperer(document.cle_stockage)
                zip_fichier.writestr(document.nom_original.lstrip("/"), contenu)

        return ContenuZip(contenu=tampon.getvalue(), nom_appel_offre=appel_offre.nom)
