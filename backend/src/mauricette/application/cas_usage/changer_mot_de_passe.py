"""Cas d'usage : changement de mot de passe d'un utilisateur."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.application.securite_mot_de_passe import hacher, verifier
from mauricette.domaine.exceptions import EntiteIntrouvable, IdentifiantsInvalides
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


@dataclass(frozen=True)
class CommandeChangerMotDePasse:
    """Données nécessaires au changement de mot de passe d'un utilisateur."""

    utilisateur_id: UUID
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str


class ChangerMotDePasse:
    """Change le mot de passe d'un utilisateur, après vérification de l'ancien."""

    def __init__(self, depot: UtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeChangerMotDePasse) -> None:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'utilisateur n'existe
        pas, `IdentifiantsInvalides` si l'ancien mot de passe fourni est incorrect."""
        utilisateur = self._depot.obtenir_par_id(commande.utilisateur_id)
        if utilisateur is None:
            raise EntiteIntrouvable(f"Utilisateur introuvable : {commande.utilisateur_id}")

        if not verifier(commande.ancien_mot_de_passe, utilisateur.mot_de_passe_hash):
            raise IdentifiantsInvalides("L'ancien mot de passe est incorrect.")

        utilisateur.changer_mot_de_passe_hash(hacher(commande.nouveau_mot_de_passe))
        self._depot.mettre_a_jour(utilisateur)
