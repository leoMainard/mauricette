"""Adaptateur PostgreSQL du port `AppelOffreRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    appel_offre_vers_entite,
    appel_offre_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import AppelOffreModele


class AppelOffreRepositorySQL(AppelOffreRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des Appels d'Offres."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, appel_offre: AppelOffre) -> None:
        self._session.add(appel_offre_vers_modele(appel_offre))
        self._session.commit()

    def obtenir_par_id(self, appel_offre_id: UUID) -> AppelOffre | None:
        modele = self._session.get(AppelOffreModele, appel_offre_id)
        return appel_offre_vers_entite(modele) if modele else None

    def lister_tous(self, terme_recherche: str | None = None) -> list[AppelOffre]:
        requete = select(AppelOffreModele).order_by(AppelOffreModele.date_creation.desc())
        if terme_recherche:
            requete = requete.where(AppelOffreModele.nom.ilike(f"%{terme_recherche}%"))
        modeles = self._session.execute(requete).scalars().all()
        return [appel_offre_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, appel_offre: AppelOffre) -> None:
        modele = self._session.get(AppelOffreModele, appel_offre.id)
        if modele is None:
            raise ValueError(f"Appel d'Offres introuvable : {appel_offre.id}")
        modele.nom = appel_offre.nom
        modele.statut = appel_offre.statut.value
        modele.date_maj = appel_offre.date_maj
        self._session.commit()
