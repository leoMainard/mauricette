"""Entité métier : Utilisateur (compte permettant de se connecter à Mauricette)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import StatutUtilisateur
from mauricette.domaine.exceptions import ErreurValidationDomaine


@dataclass
class Utilisateur:
    """Représente un compte utilisateur.

    Ne contient jamais le mot de passe en clair : seul `mot_de_passe_hash`
    (haché via bcrypt) est conservé, à la charge de la couche application.
    """

    email: str
    mot_de_passe_hash: str
    nom: str
    id: UUID = field(default_factory=uuid4)
    statut: StatutUtilisateur = StatutUtilisateur.USER
    groupe_id: UUID | None = None
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._valider_email(self.email)
        self._valider_nom(self.nom)
        self.email = self.email.strip().lower()
        self.nom = self.nom.strip()

    def renommer(self, nom: str) -> None:
        """Change le nom affiché de l'utilisateur."""
        self._valider_nom(nom)
        self.nom = nom.strip()
        self._toucher()

    def changer_email(self, email: str) -> None:
        """Change l'adresse email de connexion (l'unicité est vérifiée par le cas d'usage)."""
        self._valider_email(email)
        self.email = email.strip().lower()
        self._toucher()

    def changer_mot_de_passe_hash(self, mot_de_passe_hash: str) -> None:
        """Remplace le hash du mot de passe (le hachage est fait par la couche application)."""
        self.mot_de_passe_hash = mot_de_passe_hash
        self._toucher()

    def affecter_groupe(self, groupe_id: UUID | None) -> None:
        """Affecte l'utilisateur à un groupe (ou l'en retire si `None`)."""
        self.groupe_id = groupe_id
        self._toucher()

    @staticmethod
    def _valider_email(email: str) -> None:
        if not email or "@" not in email.strip():
            raise ErreurValidationDomaine("L'adresse email n'est pas valide.")

    @staticmethod
    def _valider_nom(nom: str) -> None:
        if not nom or not nom.strip():
            raise ErreurValidationDomaine("Le nom ne peut pas être vide.")

    def _toucher(self) -> None:
        """Met à jour la date de dernière modification."""
        self.date_maj = datetime.now(timezone.utc)
