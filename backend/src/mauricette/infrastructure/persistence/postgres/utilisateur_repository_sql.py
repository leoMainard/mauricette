"""Adaptateur PostgreSQL du port `UtilisateurRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import (
    utilisateur_vers_entite,
    utilisateur_vers_modele,
)
from mauricette.infrastructure.persistence.postgres.modeles import UtilisateurModele


class UtilisateurRepositorySQL(UtilisateurRepositoryPort):
    """Implémentation PostgreSQL (via SQLAlchemy) du repository des utilisateurs."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, utilisateur: Utilisateur) -> None:
        self._session.add(utilisateur_vers_modele(utilisateur))
        self._session.commit()

    def obtenir_par_id(self, utilisateur_id: UUID) -> Utilisateur | None:
        modele = self._session.get(UtilisateurModele, utilisateur_id)
        return utilisateur_vers_entite(modele) if modele else None

    def obtenir_par_email(self, email: str) -> Utilisateur | None:
        requete = select(UtilisateurModele).where(UtilisateurModele.email == email.strip().lower())
        modele = self._session.execute(requete).scalars().first()
        return utilisateur_vers_entite(modele) if modele else None

    def lister_tous(self) -> list[Utilisateur]:
        requete = select(UtilisateurModele).order_by(UtilisateurModele.nom)
        modeles = self._session.execute(requete).scalars().all()
        return [utilisateur_vers_entite(modele) for modele in modeles]

    def lister_ids_par_groupe(self, groupe_id: UUID) -> list[UUID]:
        requete = select(UtilisateurModele.id).where(UtilisateurModele.groupe_id == groupe_id)
        return list(self._session.execute(requete).scalars().all())

    def mettre_a_jour(self, utilisateur: Utilisateur) -> None:
        modele = self._session.get(UtilisateurModele, utilisateur.id)
        if modele is None:
            raise ValueError(f"Utilisateur introuvable : {utilisateur.id}")
        modele.email = utilisateur.email
        modele.mot_de_passe_hash = utilisateur.mot_de_passe_hash
        modele.nom = utilisateur.nom
        modele.statut = utilisateur.statut.value
        modele.groupe_id = utilisateur.groupe_id
        modele.date_maj = utilisateur.date_maj
        self._session.commit()
