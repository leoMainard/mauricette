"""Entité métier : Section d'un référentiel (regroupe des questions par thème)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class SectionReferentiel:
    """Représente une section (catégorie) au sein d'un référentiel, ex: "Franchises"."""

    referentiel_id: UUID
    nom: str
    id: UUID = field(default_factory=uuid4)
    ordre: int = 0
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._valider(self.nom)
        self.nom = self.nom.strip()

    def renommer(self, nom: str) -> None:
        """Renomme la section après validation."""
        self._valider(nom)
        self.nom = nom.strip()

    @staticmethod
    def _valider(nom: str) -> None:
        if not nom or not nom.strip():
            raise ErreurValidationDomaine("Le nom de la section ne peut pas être vide.")
