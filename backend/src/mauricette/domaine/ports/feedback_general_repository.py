"""Port (interface) pour la persistance du feedback général d'un Appel d'Offres."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.feedback_general import FeedbackGeneral


class FeedbackGeneralRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance du feedback général."""

    @abstractmethod
    def enregistrer(self, feedback: FeedbackGeneral) -> FeedbackGeneral:
        """Crée ou remplace (upsert par `appel_offre_id`) le feedback général d'un AO."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_appel_offre(self, appel_offre_id: UUID) -> FeedbackGeneral | None:
        raise NotImplementedError

    @abstractmethod
    def compter_par_avis(self) -> dict[str, int]:
        """Retourne, pour chaque valeur d'avis (positif/négatif), le nombre de feedbacks
        généraux correspondants, tous AO confondus (les AO sans avis renseigné ne sont
        pas comptés). Une seule requête agrégée, pas de N+1."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous(self) -> list[FeedbackGeneral]:
        """Retourne tous les feedbacks généraux, tous AO confondus — utilisé pour le
        bucketing temporel et le taux de couverture du tableau de bord admin."""
        raise NotImplementedError
