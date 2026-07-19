"""Cas d'usage : renommage d'une section de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeModifierSection:
    """Données nécessaires au renommage d'une section."""

    section_id: UUID
    nom: str


class ModifierSectionReferentiel:
    """Renomme une section existante."""

    def __init__(self, depot: SectionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeModifierSection) -> SectionReferentiel:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si la section n'existe pas."""
        section = self._depot.obtenir_par_id(commande.section_id)
        if section is None:
            raise EntiteIntrouvable(f"Section introuvable : {commande.section_id}")

        section.renommer(commande.nom)
        self._depot.mettre_a_jour(section)
        return section
