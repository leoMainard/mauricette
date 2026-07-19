"""Cas d'usage : dépôt d'un fichier déposé par l'utilisateur (document ou archive zip).

Ce cas d'usage orchestre `DeposerDocument` (un fichier physique -> un document) en
ajoutant des comportements transverses au-dessus :
- l'éclatement automatique des archives .zip en documents individuels, en conservant
  l'arborescence du zip (chemin relatif complet dans `nom_original`) ;
- l'ignorance des doublons (même contenu, identifié par hash SHA-256).

Le zip lui-même n'est jamais conservé comme document : seul son contenu extrait l'est.
"""

from __future__ import annotations

import hashlib
import io
import mimetypes
import posixpath
import zipfile
from dataclasses import dataclass, field
from typing import BinaryIO
from uuid import UUID

from mauricette.application.cas_usage.deposer_document import (
    CommandeDeposerDocument,
    DeposerDocument,
)
from mauricette.domaine.entites.document import Document
from mauricette.domaine.exceptions import ErreurDepotDocument
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort

# Garde-fous contre les archives excessives (ou malveillantes) : une collectivité
# dépose des dossiers d'AO, pas des jeux de données massifs.
TAILLE_MAX_ARCHIVE_DECOMPRESSEE_OCTETS = 500 * 1024 * 1024  # 500 Mo
NOMBRE_MAX_FICHIERS_PAR_ARCHIVE = 500

# Entrées techniques ajoutées par certains outils de compression, à ignorer.
PREFIXES_ENTREES_IGNOREES = ("__MACOSX/",)
NOMS_ENTREES_IGNOREES = {".DS_Store", "Thumbs.db"}


@dataclass(frozen=True)
class CommandeDeposerFichier:
    """Données nécessaires au dépôt d'un fichier (document simple ou archive)."""

    appel_offre_id: UUID
    nom_original: str
    contenu: BinaryIO
    type_mime: str


@dataclass
class ResultatDepotFichier:
    """Bilan du dépôt : documents effectivement créés et doublons ignorés."""

    documents_crees: list[Document] = field(default_factory=list)
    doublons_ignores: list[str] = field(default_factory=list)


class DeposerFichier:
    """Dépose un fichier utilisateur, en gérant l'éclatement des zips et les doublons."""

    def __init__(
        self,
        deposer_document: DeposerDocument,
        depot_documents: DocumentRepositoryPort,
    ) -> None:
        self._deposer_document = deposer_document
        self._depot_documents = depot_documents

    def executer(self, commande: CommandeDeposerFichier) -> ResultatDepotFichier:
        """Dépose le fichier ; l'éclate d'abord s'il s'agit d'une archive zip valide."""
        contenu_brut = commande.contenu.read()

        if self._est_une_archive_zip(commande.nom_original, contenu_brut):
            return self._deposer_archive(commande.appel_offre_id, contenu_brut)

        return self._deposer_fichier_unique(
            commande.appel_offre_id, commande.nom_original, contenu_brut, commande.type_mime
        )

    def _deposer_fichier_unique(
        self, appel_offre_id: UUID, nom_original: str, contenu_brut: bytes, type_mime: str
    ) -> ResultatDepotFichier:
        resultat = ResultatDepotFichier()
        hash_sha256 = hashlib.sha256(contenu_brut).hexdigest()

        if self._depot_documents.obtenir_par_hash(appel_offre_id, hash_sha256) is not None:
            resultat.doublons_ignores.append(nom_original)
            return resultat

        document = self._deposer_document.executer(
            CommandeDeposerDocument(
                appel_offre_id=appel_offre_id,
                nom_original=nom_original,
                contenu=io.BytesIO(contenu_brut),
                type_mime=type_mime,
            )
        )
        resultat.documents_crees.append(document)
        return resultat

    def _deposer_archive(self, appel_offre_id: UUID, contenu_archive: bytes) -> ResultatDepotFichier:
        resultat = ResultatDepotFichier()
        hashs_deja_deposes_dans_ce_lot: set[str] = set()

        with zipfile.ZipFile(io.BytesIO(contenu_archive)) as archive:
            entrees = self._entrees_valides(archive)
            self._verifier_taille_archive(entrees)

            for entree in entrees:
                contenu_entree = archive.read(entree)
                hash_sha256 = hashlib.sha256(contenu_entree).hexdigest()
                # Chemin relatif complet (ex: "Lot1/CCTP/cctp.pdf"), pour conserver
                # l'arborescence du zip et permettre de la reconstituer côté interface.
                chemin_relatif = entree.filename

                if (
                    hash_sha256 in hashs_deja_deposes_dans_ce_lot
                    or self._depot_documents.obtenir_par_hash(appel_offre_id, hash_sha256) is not None
                ):
                    resultat.doublons_ignores.append(chemin_relatif)
                    continue

                type_mime, _ = mimetypes.guess_type(chemin_relatif)
                document = self._deposer_document.executer(
                    CommandeDeposerDocument(
                        appel_offre_id=appel_offre_id,
                        nom_original=chemin_relatif,
                        contenu=io.BytesIO(contenu_entree),
                        type_mime=type_mime or "application/octet-stream",
                    )
                )
                hashs_deja_deposes_dans_ce_lot.add(hash_sha256)
                resultat.documents_crees.append(document)

        return resultat

    @staticmethod
    def _est_une_archive_zip(nom_original: str, contenu_brut: bytes) -> bool:
        """Une archive doit à la fois porter l'extension .zip ET être un zip valide.

        Beaucoup de formats bureautiques (.docx, .xlsx, .pptx) sont eux-mêmes des
        zips valides : sans le contrôle sur l'extension, ils seraient éclatés en
        leurs composants XML internes au lieu d'être déposés tels quels.
        """
        if not nom_original.lower().endswith(".zip"):
            return False
        return zipfile.is_zipfile(io.BytesIO(contenu_brut))

    @staticmethod
    def _entrees_valides(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
        """Filtre les dossiers, les fichiers techniques (__MACOSX, .DS_Store...)
        et les chemins dangereux (absolus ou remontant hors de l'archive, dits
        "zip slip")."""
        entrees = []
        for entree in archive.infolist():
            if entree.is_dir():
                continue
            nom_fichier = entree.filename.rsplit("/", 1)[-1]
            if entree.filename.startswith(PREFIXES_ENTREES_IGNOREES):
                continue
            if nom_fichier in NOMS_ENTREES_IGNOREES or nom_fichier.startswith("."):
                continue
            if not DeposerFichier._est_chemin_sur(entree.filename):
                continue
            entrees.append(entree)
        return entrees

    @staticmethod
    def _est_chemin_sur(chemin_zip: str) -> bool:
        """Rejette les chemins absolus ou contenant un ".." (évasion hors de l'archive)."""
        if posixpath.isabs(chemin_zip):
            return False
        return posixpath.normpath(chemin_zip).split(posixpath.sep)[0] != ".."

    @staticmethod
    def _verifier_taille_archive(entrees: list[zipfile.ZipInfo]) -> None:
        if len(entrees) > NOMBRE_MAX_FICHIERS_PAR_ARCHIVE:
            raise ErreurDepotDocument(
                f"L'archive contient trop de fichiers (max {NOMBRE_MAX_FICHIERS_PAR_ARCHIVE})."
            )
        taille_totale = sum(entree.file_size for entree in entrees)
        if taille_totale > TAILLE_MAX_ARCHIVE_DECOMPRESSEE_OCTETS:
            raise ErreurDepotDocument("L'archive dépasse la taille maximale autorisée une fois décompressée.")
