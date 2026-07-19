"""Adaptateur de stockage sur disque local.

Utile en développement (aucune dépendance externe), ou en secours. Respecte
le même port `StockageDocumentPort` que l'adaptateur S3 : basculer de l'un à
l'autre ne nécessite aucun changement dans le reste de l'application.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from mauricette.domaine.entites.enums import FournisseurStockage
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


class StockageLocal(StockageDocumentPort):
    """Stocke les documents dans un dossier du disque local."""

    def __init__(self, dossier_racine: Path) -> None:
        self._dossier_racine = dossier_racine
        self._dossier_racine.mkdir(parents=True, exist_ok=True)

    @property
    def fournisseur(self) -> FournisseurStockage:
        return FournisseurStockage.LOCAL

    def enregistrer(self, cle: str, contenu: BinaryIO, type_mime: str) -> None:
        chemin = self._chemin_absolu(cle)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with chemin.open("wb") as fichier_destination:
            fichier_destination.write(contenu.read())

    def recuperer(self, cle: str) -> bytes:
        chemin = self._chemin_absolu(cle)
        if not chemin.exists():
            raise EntiteIntrouvable(f"Fichier introuvable dans le stockage local : {cle}")
        return chemin.read_bytes()

    def supprimer(self, cle: str) -> None:
        chemin = self._chemin_absolu(cle)
        chemin.unlink(missing_ok=True)

    def generer_url_temporaire(self, cle: str, expiration_secondes: int = 3600) -> str:
        # Pas de vraie URL signée en stockage local : on retourne un chemin relatif
        # servi par une route dédiée de l'API (voir api/routes/document_routes.py).
        return f"/api/documents/fichier-local/{cle}"

    def _chemin_absolu(self, cle: str) -> Path:
        """Résout la clé logique en chemin absolu, à l'intérieur du dossier racine."""
        chemin = (self._dossier_racine / cle).resolve()
        if self._dossier_racine.resolve() not in chemin.parents and chemin != self._dossier_racine.resolve():
            raise ValueError(f"Clé de stockage invalide (hors du dossier racine) : {cle}")
        return chemin
