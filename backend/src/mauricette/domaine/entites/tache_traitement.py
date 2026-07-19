"""Entité métier : tâche de la file d'attente de traitement asynchrone RAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import StatutTache, TypeTache


@dataclass
class TacheTraitement:
    """Une tâche à exécuter par le worker RAG (extraction, découpage ou embedding d'un document).

    `reference_id` est polymorphe : selon `type_tache`, il désigne l'identifiant
    du document à traiter. Aucune contrainte de clé étrangère n'est posée en base
    pour cette raison — voir la migration correspondante.
    """

    type_tache: TypeTache
    reference_id: UUID
    id: UUID = field(default_factory=uuid4)
    statut: StatutTache = StatutTache.EN_ATTENTE
    tentatives: int = 0
    message_erreur: str | None = None
    date_prochaine_tentative: datetime | None = None
    date_reservation: datetime | None = None
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def reserver(self) -> None:
        """Marque la tâche comme réclamée par le worker courant."""
        self.statut = StatutTache.EN_COURS
        self.tentatives += 1
        self.date_reservation = datetime.now(timezone.utc)
        self._toucher()

    def reussir(self) -> None:
        self.statut = StatutTache.REUSSI
        self.message_erreur = None
        self._toucher()

    def remettre_en_attente(self, message: str, delai_secondes: int) -> None:
        """Erreur transitoire : la tâche redevient éligible après `delai_secondes`."""
        self.statut = StatutTache.EN_ATTENTE
        self.message_erreur = message
        self.date_prochaine_tentative = datetime.now(timezone.utc) + timedelta(seconds=delai_secondes)
        self._toucher()

    def echouer(self, message: str) -> None:
        """Erreur définitive (ou nombre max de tentatives atteint) : la tâche ne sera pas re-tentée."""
        self.statut = StatutTache.ECHEC
        self.message_erreur = message
        self._toucher()

    def _toucher(self) -> None:
        self.date_maj = datetime.now(timezone.utc)
