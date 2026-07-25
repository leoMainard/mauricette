"""Cas d'usage : affectation (ou retrait) d'un utilisateur à un groupe."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.groupe_utilisateur_repository import (
    GroupeUtilisateurRepositoryPort,
)
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


@dataclass(frozen=True)
class CommandeAffecterGroupeUtilisateur:
    """Données nécessaires à l'affectation d'un utilisateur à un groupe."""

    utilisateur_id: UUID
    groupe_id: UUID | None


class AffecterGroupeUtilisateur:
    """Affecte un utilisateur à un groupe, ou l'en retire si `groupe_id` est `None`."""

    def __init__(
        self,
        depot_utilisateurs: UtilisateurRepositoryPort,
        depot_groupes: GroupeUtilisateurRepositoryPort,
    ) -> None:
        self._depot_utilisateurs = depot_utilisateurs
        self._depot_groupes = depot_groupes

    def executer(self, commande: CommandeAffecterGroupeUtilisateur) -> Utilisateur:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'utilisateur ou le
        groupe visé n'existe pas."""
        utilisateur = self._depot_utilisateurs.obtenir_par_id(commande.utilisateur_id)
        if utilisateur is None:
            raise EntiteIntrouvable(f"Utilisateur introuvable : {commande.utilisateur_id}")

        if commande.groupe_id is not None:
            if self._depot_groupes.obtenir_par_id(commande.groupe_id) is None:
                raise EntiteIntrouvable(f"Groupe introuvable : {commande.groupe_id}")

        utilisateur.affecter_groupe(commande.groupe_id)
        self._depot_utilisateurs.mettre_a_jour(utilisateur)
        return utilisateur
