"""Entité métier : réponse générée par le RAG pour une question de référentiel, sur un AO donné."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import StatutReponse


@dataclass(frozen=True)
class Citation:
    """Référence à un chunk source ayant servi à générer une réponse.

    Les champs sont dénormalisés (nom du document, page, section) plutôt que de ne
    garder qu'un `chunk_id` : la citation doit rester affichable même si le chunk
    source a depuis été supprimé (relance d'un autre document, réindexation...).
    """

    chunk_id: UUID
    document_id: UUID
    document_nom: str
    page_debut: int | None
    page_fin: int | None
    titre_section: str | None


@dataclass
class ReponseQuestion:
    """Réponse générée pour une question de référentiel, dans le contexte d'un AO.

    Une seule réponse vit par (appel_offre_id, question_referentiel_id) : à chaque
    régénération, l'ancienne réponse est intégralement remplacée, jamais patchée.
    """

    appel_offre_id: UUID
    question_referentiel_id: UUID
    id: UUID = field(default_factory=uuid4)
    contenu: str | None = None
    score_confiance: float | None = None
    statut: StatutReponse = StatutReponse.GENEREE
    citations: list[Citation] = field(default_factory=list)
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def valider_par_utilisateur(self) -> None:
        """Marque la réponse comme validée par un utilisateur humain."""
        self.statut = StatutReponse.VALIDEE_UTILISATEUR
        self._toucher()

    def _toucher(self) -> None:
        self.date_maj = datetime.now(timezone.utc)
