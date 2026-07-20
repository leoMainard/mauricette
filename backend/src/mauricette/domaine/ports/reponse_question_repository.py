"""Port (interface) pour la persistance des réponses générées aux questions de référentiel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.reponse_question import ReponseQuestion


class ReponseQuestionRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des réponses."""

    @abstractmethod
    def remplacer_pour_appel_offre(
        self, appel_offre_id: UUID, reponses: list[ReponseQuestion]
    ) -> None:
        """Remplace intégralement les réponses d'un AO (supprime puis insère).

        Reflète la règle métier : une régénération est toujours complète, jamais
        un patch incrémental d'une partie des réponses.
        """
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[ReponseQuestion]:
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_appel_offre_et_question(
        self, appel_offre_id: UUID, question_referentiel_id: UUID
    ) -> ReponseQuestion | None:
        """Utilisé pour snapshotter le contenu actuel d'une réponse au moment d'un feedback."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, reponse_id: UUID) -> ReponseQuestion | None:
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, reponse: ReponseQuestion) -> None:
        """Utilisé uniquement pour les mutations en place (ex: validation par l'utilisateur)."""
        raise NotImplementedError

    @abstractmethod
    def compter_avec_contenu_par_appel_offre(self) -> dict[UUID, int]:
        """Retourne, pour chaque AO, le nombre de réponses effectivement renseignées
        (contenu non nul) — pas le nombre total de lignes `ReponseQuestion`, qui inclut
        aussi les questions sans réponse trouvée. Une seule requête agrégée, utilisée
        pour la barre de progression d'analyse dans la liste des AO.
        """
        raise NotImplementedError
