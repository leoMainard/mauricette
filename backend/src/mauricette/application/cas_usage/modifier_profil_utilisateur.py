"""Cas d'usage : modification du profil (nom, email) d'un utilisateur."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import EmailDejaUtilise, EntiteIntrouvable
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


@dataclass(frozen=True)
class CommandeModifierProfilUtilisateur:
    """Données nécessaires à la modification du profil d'un utilisateur."""

    utilisateur_id: UUID
    nom: str
    email: str


class ModifierProfilUtilisateur:
    """Met à jour le nom et l'email d'un utilisateur."""

    def __init__(self, depot: UtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeModifierProfilUtilisateur) -> Utilisateur:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'utilisateur n'existe
        pas, `EmailDejaUtilise` si le nouvel email est déjà pris par un autre compte."""
        utilisateur = self._depot.obtenir_par_id(commande.utilisateur_id)
        if utilisateur is None:
            raise EntiteIntrouvable(f"Utilisateur introuvable : {commande.utilisateur_id}")

        autre = self._depot.obtenir_par_email(commande.email)
        if autre is not None and autre.id != utilisateur.id:
            raise EmailDejaUtilise(f"Un compte existe déjà avec l'email : {commande.email}")

        utilisateur.renommer(commande.nom)
        utilisateur.changer_email(commande.email)
        self._depot.mettre_a_jour(utilisateur)
        return utilisateur
