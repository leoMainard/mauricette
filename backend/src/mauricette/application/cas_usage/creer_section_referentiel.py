"""Cas d'usage : création d'une nouvelle section dans un référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.referentiel_repository import ReferentielRepositoryPort
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeCreerSection:
    """Données nécessaires à la création d'une section."""

    referentiel_id: UUID
    nom: str


class CreerSectionReferentiel:
    """Orchestre la création et la persistance d'une nouvelle section."""

    def __init__(
        self,
        depot_sections: SectionReferentielRepositoryPort,
        depot_referentiels: ReferentielRepositoryPort,
    ) -> None:
        self._depot_sections = depot_sections
        self._depot_referentiels = depot_referentiels

    def executer(self, commande: CommandeCreerSection) -> SectionReferentiel:
        """Crée la section et la persiste, après vérification que le référentiel existe."""
        if self._depot_referentiels.obtenir_par_id(commande.referentiel_id) is None:
            raise EntiteIntrouvable(f"Référentiel introuvable : {commande.referentiel_id}")

        sections_existantes = self._depot_sections.lister_par_referentiel(commande.referentiel_id)
        section = SectionReferentiel(
            referentiel_id=commande.referentiel_id,
            nom=commande.nom,
            ordre=len(sections_existantes),
        )
        self._depot_sections.ajouter(section)
        return section
