"""Cas d'usage : enregistrer le feedback sur la réponse à une question de référentiel."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback
from mauricette.domaine.entites.feedback_reponse import FeedbackReponse
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.feedback_reponse_repository import FeedbackReponseRepositoryPort
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort


@dataclass(frozen=True)
class CommandeEnregistrerFeedbackReponse:
    """Feedback envoyé pour la réponse à une question de référentiel (état courant, remplace le précédent)."""

    appel_offre_id: UUID
    question_referentiel_id: UUID
    avis: Avis | None
    commentaire: str | None
    source_attendue: str | None
    citation_attendue: str | None
    type_erreur: TypeErreurFeedback | None
    details_erreur: str | None


class EnregistrerFeedbackReponse:
    """Enregistre (crée ou remplace) le feedback sur la réponse à une question de référentiel.

    Rattaché à (appel_offre_id, question_referentiel_id), pas à l'id éphémère de
    `ReponseQuestion` (survit à une régénération complète des réponses). Le
    contenu actuel de la réponse est snapshoté au moment de l'envoi, pour
    permettre de détecter côté frontend si la réponse a changé depuis.
    """

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_reponses: ReponseQuestionRepositoryPort,
        depot_feedback: FeedbackReponseRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_reponses = depot_reponses
        self._depot_feedback = depot_feedback

    def executer(self, commande: CommandeEnregistrerFeedbackReponse) -> FeedbackReponse:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        if self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id) is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        reponse_actuelle = self._depot_reponses.obtenir_par_appel_offre_et_question(
            commande.appel_offre_id, commande.question_referentiel_id
        )

        feedback = FeedbackReponse(
            appel_offre_id=commande.appel_offre_id,
            question_referentiel_id=commande.question_referentiel_id,
            avis=commande.avis,
            contenu_reponse_snapshot=reponse_actuelle.contenu if reponse_actuelle else None,
            commentaire=commande.commentaire,
            source_attendue=commande.source_attendue,
            citation_attendue=commande.citation_attendue,
            type_erreur=commande.type_erreur,
            details_erreur=commande.details_erreur,
        )
        return self._depot_feedback.enregistrer(feedback)
