"""Cas d'usage : consultation de tous les groupes d'utilisateurs."""

from __future__ import annotations

from mauricette.domaine.entites.groupe_utilisateur import GroupeUtilisateur
from mauricette.domaine.ports.groupe_utilisateur_repository import (
    GroupeUtilisateurRepositoryPort,
)


class ListerGroupesUtilisateur:
    """Retourne tous les groupes d'utilisateurs existants."""

    def __init__(self, depot: GroupeUtilisateurRepositoryPort) -> None:
        self._depot = depot

    def executer(self) -> list[GroupeUtilisateur]:
        return self._depot.lister_tous()
