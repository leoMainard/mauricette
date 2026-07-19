"""Adaptateur PostgreSQL du port `TacheTraitementRepositoryPort`.

La réclamation de tâche (`reclamer_tache_suivante`) utilise un verrou
`SELECT ... FOR UPDATE SKIP LOCKED` pour permettre à plusieurs workers de
tourner en concurrence sans jamais traiter deux fois la même tâche.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.enums import StatutTache, TypeTache
from mauricette.domaine.entites.tache_traitement import TacheTraitement
from mauricette.domaine.ports.tache_traitement_repository import TacheTraitementRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    tache_traitement_vers_entite,
    tache_traitement_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import TacheTraitementModele


class TacheTraitementRepositorySQL(TacheTraitementRepositoryPort):
    """Implémentation PostgreSQL de la file d'attente de traitement RAG."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def enqueuer(self, type_tache: TypeTache, reference_id: UUID) -> TacheTraitement:
        entite = TacheTraitement(type_tache=type_tache, reference_id=reference_id)
        self._session.add(tache_traitement_vers_modele(entite))
        self._session.commit()
        return entite

    def obtenir_en_cours_ou_en_attente(
        self, type_tache: TypeTache, reference_id: UUID
    ) -> TacheTraitement | None:
        requete = select(TacheTraitementModele).where(
            TacheTraitementModele.type_tache == type_tache.value,
            TacheTraitementModele.reference_id == reference_id,
            TacheTraitementModele.statut.in_([StatutTache.EN_ATTENTE.value, StatutTache.EN_COURS.value]),
        )
        modele = self._session.execute(requete).scalars().first()
        return tache_traitement_vers_entite(modele) if modele else None

    def reclamer_tache_suivante(self, types_geres: list[TypeTache]) -> TacheTraitement | None:
        requete = (
            select(TacheTraitementModele)
            .where(
                TacheTraitementModele.statut == StatutTache.EN_ATTENTE.value,
                TacheTraitementModele.type_tache.in_([type_tache.value for type_tache in types_geres]),
                or_(
                    TacheTraitementModele.date_prochaine_tentative.is_(None),
                    TacheTraitementModele.date_prochaine_tentative <= func.now(),
                ),
            )
            .order_by(TacheTraitementModele.date_creation)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        modele = self._session.execute(requete).scalars().first()
        if modele is None:
            self._session.commit()
            return None

        modele.statut = StatutTache.EN_COURS.value
        modele.tentatives += 1
        modele.date_reservation = datetime.now(timezone.utc)
        self._session.commit()
        return tache_traitement_vers_entite(modele)

    def marquer_reussie(self, tache_id: UUID) -> None:
        modele = self._session.get(TacheTraitementModele, tache_id)
        if modele is None:
            raise ValueError(f"Tâche introuvable : {tache_id}")
        modele.statut = StatutTache.REUSSI.value
        modele.message_erreur = None
        self._session.commit()

    def remettre_en_attente(self, tache_id: UUID, message_erreur: str, delai_secondes: int) -> None:
        modele = self._session.get(TacheTraitementModele, tache_id)
        if modele is None:
            raise ValueError(f"Tâche introuvable : {tache_id}")
        modele.statut = StatutTache.EN_ATTENTE.value
        modele.message_erreur = message_erreur
        modele.date_prochaine_tentative = datetime.now(timezone.utc) + timedelta(seconds=delai_secondes)
        self._session.commit()

    def marquer_echouee(self, tache_id: UUID, message_erreur: str) -> None:
        modele = self._session.get(TacheTraitementModele, tache_id)
        if modele is None:
            raise ValueError(f"Tâche introuvable : {tache_id}")
        modele.statut = StatutTache.ECHEC.value
        modele.message_erreur = message_erreur
        self._session.commit()
