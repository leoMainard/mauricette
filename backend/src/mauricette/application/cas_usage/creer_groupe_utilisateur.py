"""Cas d'usage : création d'un groupe d'utilisateurs."""

from __future__ import annotations

from dataclasses import dataclass

from mauricette.domaine.entites.groupe_utilisateur import GroupeUtilisateur
from mauricette.domaine.ports.groupe_utilisateur_repository import (
    GroupeUtilisateurRepositoryPort,
)


@dataclass(frozen=True)
class CommandeCreerGroupeUtilisateur:
    """Données nécessaires à la création d'un groupe d'utilisateurs."""

    nom: str


class CreerGroupeUtilisateur:
    """Orchestre la création et la persistance d'un nouveau groupe d'utilisateurs."""

    def __init__(self, depot: GroupeUtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeCreerGroupeUtilisateur) -> GroupeUtilisateur:
        """Crée le groupe et le persiste."""
        groupe = GroupeUtilisateur(nom=commande.nom)
        self._depot.ajouter(groupe)
        return groupe
