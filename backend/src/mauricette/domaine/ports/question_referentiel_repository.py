"""Port (interface) pour la persistance des Questions de référentiel."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from mauricette.domaine.entites.question_referentiel import QuestionReferentiel


class QuestionReferentielRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des questions."""

    @abstractmethod
    def ajouter(self, question: QuestionReferentiel) -> None:
        """Persiste une nouvelle question."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, question_id: UUID) -> QuestionReferentiel | None:
        """Retourne la question correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_section(self, section_id: UUID) -> list[QuestionReferentiel]:
        """Retourne les questions d'une section, triées par ordre."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_referentiel(self, referentiel_id: UUID) -> list[QuestionReferentiel]:
        """Retourne toutes les questions d'un référentiel (toutes sections confondues)."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, question: QuestionReferentiel) -> None:
        """Enregistre les modifications apportées à une question existante."""
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, question_id: UUID) -> None:
        """Supprime définitivement une question."""
        raise NotImplementedError

    @abstractmethod
    def compter_actives_par_referentiel(self) -> dict[UUID, int]:
        """Retourne, pour chaque référentiel, son nombre de questions actives.

        Une seule requête agrégée pour tous les référentiels (pas de N+1).
        """
        raise NotImplementedError
