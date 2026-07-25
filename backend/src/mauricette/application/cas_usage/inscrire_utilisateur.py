"""Cas d'usage : inscription d'un nouvel utilisateur."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.application.securite_mot_de_passe import hacher
from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import EmailDejaUtilise
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


@dataclass(frozen=True)
class CommandeInscrireUtilisateur:
    """Données nécessaires à l'inscription d'un utilisateur."""

    email: str
    mot_de_passe: str
    nom: str


class InscrireUtilisateur:
    """Crée un nouveau compte utilisateur (statut USER par défaut)."""

    def __init__(self, depot: UtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeInscrireUtilisateur) -> Utilisateur:
        """Exécute le cas d'usage, lève `EmailDejaUtilise` si l'email est déjà pris."""
        if self._depot.obtenir_par_email(commande.email) is not None:
            raise EmailDejaUtilise(f"Un compte existe déjà avec l'email : {commande.email}")

        utilisateur = Utilisateur(
            email=commande.email,
            mot_de_passe_hash=hacher(commande.mot_de_passe),
            nom=commande.nom,
        )
        self._depot.ajouter(utilisateur)
        return utilisateur
