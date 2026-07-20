"""Cas d'usage : enregistrer le feedback général d'un AO."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import Avis
from mauricette.domaine.entites.feedback_general import FeedbackGeneral
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.feedback_general_repository import FeedbackGeneralRepositoryPort


@dataclass(frozen=True)
class CommandeEnregistrerFeedbackGeneral:
    """Feedback général envoyé pour un AO (état courant, remplace le précédent)."""

    appel_offre_id: UUID
    avis: Avis | None
    commentaire: str | None


class EnregistrerFeedbackGeneral:
    """Enregistre (crée ou remplace) le feedback général d'un AO."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_feedback: FeedbackGeneralRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_feedback = depot_feedback

    def executer(self, commande: CommandeEnregistrerFeedbackGeneral) -> FeedbackGeneral:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        feedback = FeedbackGeneral(
            appel_offre_id=commande.appel_offre_id,
            avis=commande.avis,
            commentaire=commande.commentaire,
        )
        return self._depot_feedback.enregistrer(feedback)
