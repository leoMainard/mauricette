"""Cas d'usage : connexion d'un utilisateur (vérification email/mot de passe)."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.application.securite_mot_de_passe import verifier
from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import IdentifiantsInvalides
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


@dataclass(frozen=True)
class CommandeConnecterUtilisateur:
    """Données nécessaires à la connexion d'un utilisateur."""

    email: str
    mot_de_passe: str


class ConnecterUtilisateur:
    """Vérifie les identifiants et retourne l'utilisateur correspondant."""

    def __init__(self, depot: UtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeConnecterUtilisateur) -> Utilisateur:
        """Exécute le cas d'usage, lève `IdentifiantsInvalides` si l'email/mot de
        passe ne correspondent à aucun compte (message volontairement identique
        dans les deux cas, pour ne pas révéler si l'email existe)."""
        utilisateur = self._depot.obtenir_par_email(commande.email)
        if utilisateur is None or not verifier(commande.mot_de_passe, utilisateur.mot_de_passe_hash):
            raise IdentifiantsInvalides("Email ou mot de passe incorrect.")
        return utilisateur
