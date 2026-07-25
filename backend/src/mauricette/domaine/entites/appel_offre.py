"""Entité métier : Appel d'Offres."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import StatutAppelOffre
from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class AppelOffre:
    """Représente un Appel d'Offres déposé par un utilisateur.

    Un Appel d'Offres regroupe un ensemble de documents (cahier des charges,
    annexes, etc.) sur lesquels des questions pourront être posées via le RAG.
    """

    nom: str
    cree_par: str
    cree_par_id: UUID
    id: UUID = field(default_factory=uuid4)
    statut: StatutAppelOffre = StatutAppelOffre.BROUILLON
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.nom or not self.nom.strip():
            raise ErreurValidationDomaine("Le nom de l'Appel d'Offres ne peut pas être vide.")
        self.nom = self.nom.strip()

    def passer_en_cours(self) -> None:
        """Fait passer l'AO en statut 'en cours' (dépôt de documents démarré)."""
        self.statut = StatutAppelOffre.EN_COURS
        self._toucher()

    def marquer_traite(self) -> None:
        """Fait passer l'AO en statut 'traité' (tous les documents indexés)."""
        self.statut = StatutAppelOffre.TRAITE
        self._toucher()

    def archiver(self) -> None:
        """Archive l'AO."""
        self.statut = StatutAppelOffre.ARCHIVE
        self._toucher()

    def renommer(self, nouveau_nom: str) -> None:
        """Renomme l'AO en validant que le nouveau nom n'est pas vide."""
        if not nouveau_nom or not nouveau_nom.strip():
            raise ErreurValidationDomaine("Le nom de l'Appel d'Offres ne peut pas être vide.")
        self.nom = nouveau_nom.strip()
        self._toucher()

    def _toucher(self) -> None:
        """Met à jour la date de dernière modification."""
        self.date_maj = datetime.now(timezone.utc)
