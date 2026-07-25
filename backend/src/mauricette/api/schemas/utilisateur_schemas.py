"""Schémas Pydantic (contrats HTTP) pour les utilisateurs et les groupes d'utilisateurs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from mauricette.domaine.entites.enums import StatutUtilisateur
from mauricette.domaine.entites.groupe_utilisateur import GroupeUtilisateur
from mauricette.domaine.entites.utilisateur import Utilisateur

# --- Utilisateur ---


class InscriptionRequete(BaseModel):
    """Corps de requête pour l'inscription d'un nouvel utilisateur."""

    email: EmailStr
    mot_de_passe: str = Field(min_length=8, max_length=255)
    nom: str = Field(min_length=1, max_length=255)


class ConnexionRequete(BaseModel):
    """Corps de requête pour la connexion d'un utilisateur."""

    email: EmailStr
    mot_de_passe: str = Field(min_length=1, max_length=255)


class ModificationProfilRequete(BaseModel):
    """Corps de requête pour la modification du profil (nom, email)."""

    nom: str = Field(min_length=1, max_length=255)
    email: EmailStr


class ChangementMotDePasseRequete(BaseModel):
    """Corps de requête pour le changement de mot de passe."""

    ancien_mot_de_passe: str = Field(min_length=1, max_length=255)
    nouveau_mot_de_passe: str = Field(min_length=8, max_length=255)


class AffectationGroupeRequete(BaseModel):
    """Corps de requête pour affecter un utilisateur à un groupe (ou l'en retirer)."""

    groupe_id: UUID | None = None


class UtilisateurReponse(BaseModel):
    """Représentation HTTP d'un utilisateur (ne contient jamais le mot de passe/hash)."""

    id: UUID
    email: str
    nom: str
    statut: StatutUtilisateur
    groupe_id: UUID | None
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, entite: Utilisateur) -> "UtilisateurReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=entite.id,
            email=entite.email,
            nom=entite.nom,
            statut=entite.statut,
            groupe_id=entite.groupe_id,
            date_creation=entite.date_creation,
            date_maj=entite.date_maj,
        )


# --- Groupe d'utilisateurs ---


class CreationGroupeRequete(BaseModel):
    """Corps de requête pour la création d'un groupe d'utilisateurs."""

    nom: str = Field(min_length=1, max_length=255)


class GroupeUtilisateurReponse(BaseModel):
    """Représentation HTTP d'un groupe d'utilisateurs."""

    id: UUID
    nom: str
    date_creation: datetime

    @classmethod
    def depuis_entite(cls, entite: GroupeUtilisateur) -> "GroupeUtilisateurReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(id=entite.id, nom=entite.nom, date_creation=entite.date_creation)
