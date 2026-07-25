"""Adaptateur PostgreSQL du port `GroupeUtilisateurRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.groupe_utilisateur import GroupeUtilisateur
from mauricette.domaine.ports.groupe_utilisateur_repository import (
    GroupeUtilisateurRepositoryPort,
)
from mauricette.infrastructure.persistence.postgres.mappers import (
    groupe_utilisateur_vers_entite,
    groupe_utilisateur_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import GroupeUtilisateurModele


class GroupeUtilisateurRepositorySQL(GroupeUtilisateurRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des groupes d'utilisateurs."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, groupe: GroupeUtilisateur) -> None:
        self._session.add(groupe_utilisateur_vers_modele(groupe))
        self._session.commit()

    def obtenir_par_id(self, groupe_id: UUID) -> GroupeUtilisateur | None:
        modele = self._session.get(GroupeUtilisateurModele, groupe_id)
        return groupe_utilisateur_vers_entite(modele) if modele else None

    def lister_tous(self) -> list[GroupeUtilisateur]:
        requete = select(GroupeUtilisateurModele).order_by(GroupeUtilisateurModele.nom)
        modeles = self._session.execute(requete).scalars().all()
        return [groupe_utilisateur_vers_entite(modele) for modele in modeles]

    def mettre_a_jour(self, groupe: GroupeUtilisateur) -> None:
        modele = self._session.get(GroupeUtilisateurModele, groupe.id)
        if modele is None:
            raise ValueError(f"Groupe introuvable : {groupe.id}")
        modele.nom = groupe.nom
        self._session.commit()
