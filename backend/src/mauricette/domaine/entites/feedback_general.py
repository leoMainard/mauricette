"""Entité métier : avis général de l'utilisateur sur l'aide apportée par Mauricette pour un AO."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import Avis


@dataclass
class FeedbackGeneral:
    """Avis global sur l'aide apportée par Mauricette pour un AO.

    Un seul feedback par AO : un nouvel envoi remplace le précédent (état
    courant remplaçable, pas un journal historique).
    """

    appel_offre_id: UUID
    avis: Avis | None = None
    commentaire: str | None = None
    id: UUID = field(default_factory=uuid4)
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
