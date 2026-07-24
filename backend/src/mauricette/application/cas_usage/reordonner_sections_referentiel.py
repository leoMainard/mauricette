"""Cas d'usage : réordonnancement des sections d'un référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurValidationDomaine
from mauricette.domaine.ports.section_referentiel_repository import (
    SectionReferentielRepositoryPort,
)


@dataclass(frozen=True)
class CommandeReordonnerSections:
    """Données nécessaires au réordonnancement des sections d'un référentiel."""

    referentiel_id: UUID
    ids_ordonnes: list[UUID]


class ReordonnerSectionsReferentiel:
    """Applique un nouvel ordre d'affichage aux sections d'un référentiel."""

    def __init__(self, depot: SectionReferentielRepositoryPort) -> None:
        self._depot = depot

    def executer(self, commande: CommandeReordonnerSections) -> list[SectionReferentiel]:
        """Persiste le nouvel ordre, après vérification que la liste soumise correspond
        exactement aux sections existantes (ni id manquant, ni id étranger, ni doublon)."""
        existantes = self._depot.lister_par_referentiel(commande.referentiel_id)
        if not existantes:
            raise EntiteIntrouvable(
                f"Référentiel introuvable ou sans section : {commande.referentiel_id}"
            )

        soumis = commande.ids_ordonnes
        if len(soumis) != len(set(soumis)):
            raise ErreurValidationDomaine("La liste d'ordre contient des identifiants en double.")
        if set(soumis) != {section.id for section in existantes}:
            raise ErreurValidationDomaine(
                "La liste soumise ne correspond pas exactement aux sections existantes."
            )

        par_id = {section.id: section for section in existantes}
        for index, section_id in enumerate(soumis):
            par_id[section_id].ordre = index
            self._depot.mettre_a_jour(par_id[section_id])
        return [par_id[section_id] for section_id in soumis]
