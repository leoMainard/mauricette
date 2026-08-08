"""Entité métier : avis de l'utilisateur sur la réponse générée à une question de référentiel."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from mauricette.domaine.entites.enums import Avis, TypeErreurFeedback


@dataclass
class FeedbackReponse:
    """Avis sur la réponse à une question de référentiel donnée, pour un AO.

    Rattaché à (appel_offre_id, question_referentiel_id) plutôt qu'à l'id
    éphémère de `ReponseQuestion` : une régénération remplace intégralement
    toutes les réponses d'un AO (`remplacer_pour_appel_offre`), donc un
    feedback lié à l'instance précise serait perdu à chaque régénération.
    `contenu_reponse_snapshot` capture le texte de la réponse au moment du
    feedback, pour détecter si elle a changé depuis (comparaison côté
    frontend avec le contenu actuel).

    Un seul feedback par (appel_offre_id, question_referentiel_id) : un
    nouvel envoi remplace le précédent.
    """

    appel_offre_id: UUID
    question_referentiel_id: UUID
    avis: Avis | None = None
    contenu_reponse_snapshot: str | None = None
    commentaire: str | None = None
    sources_attendues_ids: list[UUID] = field(default_factory=list)
    citation_attendue: str | None = None
    types_erreur: list[TypeErreurFeedback] = field(default_factory=list)
    details_erreur: str | None = None
    id: UUID = field(default_factory=uuid4)
    date_creation: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_maj: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
