"""Cas d'usage : consultation de tous les utilisateurs (administration)."""

from __future__ import annotations

from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.ports.utilisateur_repository import UtilisateurRepositoryPort


class ListerUtilisateurs:
    """Retourne tous les utilisateurs existants."""

    def __init__(self, depot: UtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self) -> list[Utilisateur]:
        return self._depot.lister_tous()
