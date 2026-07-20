"""Cas d'usage : validation manuelle d'une réponse générée par un utilisateur."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.reponse_question import ReponseQuestion
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort


@dataclass(frozen=True)
class CommandeValiderReponse:
    """Identifie la réponse à valider."""

    reponse_id: UUID


class ValiderReponse:
    """Marque une réponse générée comme validée par un utilisateur humain."""

    def __init__(self, depot_reponses: ReponseQuestionRepositoryPort) -> None:
        self._depot_reponses = depot_reponses

    def executer(self, commande: CommandeValiderReponse) -> ReponseQuestion:
        reponse = self._depot_reponses.obtenir_par_id(commande.reponse_id)
        if reponse is None:
            raise EntiteIntrouvable(f"Réponse introuvable : {commande.reponse_id}")
        reponse.valider_par_utilisateur()
        self._depot_reponses.mettre_a_jour(reponse)
        return reponse
