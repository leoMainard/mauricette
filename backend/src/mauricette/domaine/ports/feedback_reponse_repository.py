"""Port (interface) pour la persistance du feedback sur les réponses générées."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback
from mauricette.domaine.entites.feedback_reponse import FeedbackReponse


@dataclass(frozen=True)
class FeedbackReponseDetaille:
    """Un feedback par réponse, enrichi du contexte nécessaire à son analyse
    (AO, référentiel, question) — évite au tableau de bord admin de devoir
    recharger chaque référentiel séparément pour retrouver ces libellés."""

    id: UUID
    appel_offre_id: UUID
    appel_offre_nom: str
    referentiel_id: UUID
    referentiel_nom: str
    question_referentiel_id: UUID
    question: str
    avis: Avis | None
    commentaire: str | None
    contenu_reponse_snapshot: str | None
    source_attendue: str | None
    citation_attendue: str | None
    type_erreur: TypeErreurFeedback | None
    details_erreur: str | None
    date_creation: datetime


class FeedbackReponseRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance du feedback par réponse."""

    @abstractmethod
    def enregistrer(self, feedback: FeedbackReponse) -> FeedbackReponse:
        """Crée ou remplace (upsert par `(appel_offre_id, question_referentiel_id)`)."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[FeedbackReponse]:
        """Une seule requête agrégée pour tous les feedbacks de l'AO (pas de N+1),
        utilisée pour préremplir l'état des pouces à l'ouverture de l'onglet Questions.
        """
        raise NotImplementedError

    @abstractmethod
    def compter_par_avis(self) -> dict[str, int]:
        """Retourne, pour chaque valeur d'avis (positif/négatif), le nombre de feedbacks
        par réponse correspondants, tous AO confondus. Une seule requête agrégée."""
        raise NotImplementedError

    @abstractmethod
    def compter_par_type_erreur(self) -> dict[str, int]:
        """Retourne, pour chaque type d'erreur renseigné, le nombre de feedbacks négatifs
        détaillés correspondants, tous AO confondus. Une seule requête agrégée."""
        raise NotImplementedError

    @abstractmethod
    def compter_negatifs_par_referentiel(self) -> dict[UUID, int]:
        """Retourne, pour chaque référentiel, le nombre de feedbacks négatifs parmi ses
        questions — jointure vers question_referentiel puis section_referentiel,
        une seule requête agrégée."""
        raise NotImplementedError

    @abstractmethod
    def lister_tous_avec_contexte(self) -> list[FeedbackReponseDetaille]:
        """Retourne tous les feedbacks par réponse, tous AO confondus, enrichis du nom
        de l'AO, du référentiel et de l'intitulé de la question — une seule requête
        agrégée (jointures appel_offre + question_referentiel + section_referentiel),
        utilisée pour l'analyse détaillée et le filtrage par référentiel/question du
        tableau de bord admin."""
        raise NotImplementedError
