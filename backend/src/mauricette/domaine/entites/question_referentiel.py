"""Entité métier : Question d'une section de référentiel."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class QuestionReferentiel:
    """Représente une question rattachée à une section d'un référentiel.

    `aide_extraction` n'a pas de rôle pour l'utilisateur qui rédige la
    question ; elle sert à guider le RAG lors de la recherche et de la
    rédaction de la réponse (ex: "cherche dans le CCTP la clause de franchise").
    """

    section_id: UUID
    question: str
    format_reponse: FormatReponse
    id: UUID = field(default_factory=uuid4)
    aide_extraction: str | None = None
    obligatoire: bool = False
    actif: bool = True
    ordre: int = 0
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._valider(self.question)
        self.question = self.question.strip()

    def modifier(
        self,
        question: str,
        format_reponse: FormatReponse,
        aide_extraction: str | None,
        obligatoire: bool,
    ) -> None:
        """Met à jour le contenu de la question après validation."""
        self._valider(question)
        self.question = question.strip()
        self.format_reponse = format_reponse
        self.aide_extraction = aide_extraction
        self.obligatoire = obligatoire
        self._toucher()

    def archiver(self) -> None:
        """Désactive la question sans la supprimer."""
        self.actif = False
        self._toucher()

    def reactiver(self) -> None:
        """Réactive une question archivée."""
        self.actif = True
        self._toucher()

    @staticmethod
    def _valider(question: str) -> None:
        if not question or not question.strip():
            raise ErreurValidationDomaine("L'intitulé de la question ne peut pas être vide.")

    def _toucher(self) -> None:
        """Met à jour la date de dernière modification."""
        self.date_maj = datetime.now(timezone.utc)
