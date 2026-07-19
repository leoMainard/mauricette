"""Entité métier : Document rattaché à un Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import FournisseurStockage, StatutDocument
from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class Document:
    """Représente un fichier déposé dans le cadre d'un Appel d'Offres.

    Le document ne contient jamais le contenu binaire du fichier : celui-ci vit
    dans le stockage (local ou S3/MinIO) et est référencé ici par `cle_stockage`.
    Cette séparation permet de changer de fournisseur de stockage sans toucher
    au modèle métier.
    """

    appel_offre_id: UUID
    nom_original: str
    cle_stockage: str
    fournisseur_stockage: FournisseurStockage
    type_mime: str
    taille_octets: int
    id: UUID = field(default_factory=uuid4)
    hash_sha256: str | None = None
    statut: StatutDocument = StatutDocument.EN_ATTENTE
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.nom_original or not self.nom_original.strip():
            raise ErreurValidationDomaine("Le nom du document ne peut pas être vide.")
        if self.taille_octets < 0:
            raise ErreurValidationDomaine("La taille d'un document ne peut pas être négative.")

    def marquer_televerse(self) -> None:
        """Confirme que le fichier a bien été écrit dans le stockage."""
        self.statut = StatutDocument.TELEVERSE
        self._toucher()

    def marquer_en_erreur(self) -> None:
        """Marque le document en erreur (échec de téléversement ou de traitement)."""
        self.statut = StatutDocument.EN_ERREUR
        self._toucher()

    def marquer_traite(self) -> None:
        """Marque le document comme traité (découpé en chunks et indexé)."""
        self.statut = StatutDocument.TRAITE
        self._toucher()

    def _toucher(self) -> None:
        """Met à jour la date de dernière modification."""
        self.date_maj = datetime.now(timezone.utc)
