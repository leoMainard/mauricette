"""Entité métier : suivi du traitement RAG d'un document (extraction, découpage, embedding)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from mauricette.domaine.entites.enums import StatutEtape


@dataclass
class DocumentTraitementRag:
    """Suivi de l'avancement du pipeline RAG pour un document donné.

    Extension 1:1 de `Document`, volontairement séparée de celui-ci : le cycle
    de vie du dépôt (`StatutDocument`) et celui du traitement RAG sont deux
    préoccupations distinctes qui évoluent indépendamment. Chaque étape porte
    son propre statut et son propre message d'erreur, pour éviter un statut
    global opaque qui masquerait où le pipeline a échoué.
    """

    document_id: UUID
    appel_offre_id: UUID

    extraction_statut: StatutEtape = StatutEtape.EN_ATTENTE
    extraction_message_erreur: str | None = None
    extraction_date_maj: datetime | None = None

    decoupage_statut: StatutEtape = StatutEtape.EN_ATTENTE
    decoupage_message_erreur: str | None = None
    decoupage_date_maj: datetime | None = None

    embedding_statut: StatutEtape = StatutEtape.EN_ATTENTE
    embedding_message_erreur: str | None = None
    embedding_date_maj: datetime | None = None

    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def demarrer_extraction(self) -> None:
        self.extraction_statut = StatutEtape.EN_COURS
        self.extraction_message_erreur = None
        self._toucher(marquer_extraction=True)

    def reussir_extraction(self) -> None:
        self.extraction_statut = StatutEtape.REUSSI
        self.extraction_message_erreur = None
        self._toucher(marquer_extraction=True)

    def echouer_extraction(self, message: str) -> None:
        self.extraction_statut = StatutEtape.ECHEC
        self.extraction_message_erreur = message
        self._toucher(marquer_extraction=True)

    def demarrer_decoupage(self) -> None:
        self.decoupage_statut = StatutEtape.EN_COURS
        self.decoupage_message_erreur = None
        self._toucher(marquer_decoupage=True)

    def reussir_decoupage(self) -> None:
        self.decoupage_statut = StatutEtape.REUSSI
        self.decoupage_message_erreur = None
        self._toucher(marquer_decoupage=True)

    def echouer_decoupage(self, message: str) -> None:
        self.decoupage_statut = StatutEtape.ECHEC
        self.decoupage_message_erreur = message
        self._toucher(marquer_decoupage=True)

    def demarrer_embedding(self) -> None:
        self.embedding_statut = StatutEtape.EN_COURS
        self.embedding_message_erreur = None
        self._toucher(marquer_embedding=True)

    def reussir_embedding(self) -> None:
        self.embedding_statut = StatutEtape.REUSSI
        self.embedding_message_erreur = None
        self._toucher(marquer_embedding=True)

    def echouer_embedding(self, message: str) -> None:
        self.embedding_statut = StatutEtape.ECHEC
        self.embedding_message_erreur = message
        self._toucher(marquer_embedding=True)

    def reinitialiser(self) -> None:
        """Remet les 3 étapes à `EN_ATTENTE` et efface les messages : utilisé par une relance."""
        self.extraction_statut = StatutEtape.EN_ATTENTE
        self.extraction_message_erreur = None
        self.decoupage_statut = StatutEtape.EN_ATTENTE
        self.decoupage_message_erreur = None
        self.embedding_statut = StatutEtape.EN_ATTENTE
        self.embedding_message_erreur = None
        self._toucher()

    @property
    def statut_global(self) -> StatutEtape:
        """Résume les 3 étapes en un seul statut, pour l'affichage et le calcul de progression."""
        etapes = (self.extraction_statut, self.decoupage_statut, self.embedding_statut)
        if StatutEtape.ECHEC in etapes:
            return StatutEtape.ECHEC
        if all(etape == StatutEtape.REUSSI for etape in etapes):
            return StatutEtape.REUSSI
        if StatutEtape.EN_COURS in etapes:
            return StatutEtape.EN_COURS
        return StatutEtape.EN_ATTENTE

    def _toucher(
        self,
        *,
        marquer_extraction: bool = False,
        marquer_decoupage: bool = False,
        marquer_embedding: bool = False,
    ) -> None:
        maintenant = datetime.now(timezone.utc)
        if marquer_extraction:
            self.extraction_date_maj = maintenant
        if marquer_decoupage:
            self.decoupage_date_maj = maintenant
        if marquer_embedding:
            self.embedding_date_maj = maintenant
        self.date_maj = maintenant
