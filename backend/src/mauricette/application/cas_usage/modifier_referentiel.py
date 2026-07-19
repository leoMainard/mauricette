"""Cas d'usage : modification d'un référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort


@dataclass(frozen=True)
class CommandeModifierReferentiel:
    """Données nécessaires à la modification d'un référentiel."""

    referentiel_id: UUID
    nom: str
    description: str | None
    actif_par_defaut: bool


class ModifierReferentiel:
    """Modifie le contenu d'un référentiel existant."""

    def __init__(self, depot: ReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeModifierReferentiel) -> Referentiel:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si le référentiel n'existe pas."""
        referentiel = self._depot.obtenir_par_id(commande.referentiel_id)
        if referentiel is None:
            raise EntiteIntrouvable(f"Référentiel introuvable : {commande.referentiel_id}")

        referentiel.modifier(
            nom=commande.nom,
            description=commande.description,
            actif_par_defaut=commande.actif_par_defaut,
        )
        self._depot.mettre_a_jour(referentiel)
        return referentiel
