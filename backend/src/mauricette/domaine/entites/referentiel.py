"""Entité métier : Référentiel (collection nommée de sections et de questions)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class Referentiel:
    """Représente un référentiel de questions : un ensemble nommé, organisé en
    sections, que l'utilisateur peut appliquer à ses Appels d'Offres.

    Un référentiel marqué `actif_par_defaut` est automatiquement rattaché à
    tout nouvel Appel d'Offres ; l'utilisateur peut toujours en rattacher
    d'autres manuellement par la suite.
    """

    nom: str
    cree_par_id: UUID
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    actif_par_defaut: bool = False
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._valider(self.nom)
        self.nom = self.nom.strip()

    def modifier(self, nom: str, description: str | None, actif_par_defaut: bool) -> None:
        """Met à jour le contenu du référentiel après validation."""
        self._valider(nom)
        self.nom = nom.strip()
        self.description = description
        self.actif_par_defaut = actif_par_defaut
        self._toucher()

    @staticmethod
    def _valider(nom: str) -> None:
        if not nom or not nom.strip():
            raise ErreurValidationDomaine("Le nom du référentiel ne peut pas être vide.")

    def _toucher(self) -> None:
        """Met à jour la date de dernière modification."""
        self.date_maj = datetime.now(timezone.utc)
