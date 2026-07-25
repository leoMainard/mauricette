"""Cas d'usage : création d'un nouveau référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort


@dataclass(frozen=True)
class CommandeCreerReferentiel:
    """Données nécessaires à la création d'un référentiel."""

    nom: str
    cree_par_id: UUID
    description: str | None = None
    actif_par_defaut: bool = False


class CreerReferentiel:
    """Orchestre la création et la persistance d'un nouveau référentiel."""

    def __init__(self, depot: ReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeCreerReferentiel) -> Referentiel:
        """Crée le référentiel et le persiste via le repository."""
        referentiel = Referentiel(
            nom=commande.nom,
            cree_par_id=commande.cree_par_id,
            description=commande.description,
            actif_par_defaut=commande.actif_par_defaut,
        )
        self._depot.ajouter(referentiel)
        return referentiel
