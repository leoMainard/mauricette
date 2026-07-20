"""Adaptateur de génération de réponses basé sur l'API Mistral (Mistral Large)."""

from __future__ import annotations

import json

from mistralai.client import Mistral
from mistralai.client.errors.mistralerror import MistralError

from mauricette.config.parametres import Parametres
from mauricette.domaine.entites.enums import FormatReponse
from mauricette.domaine.exceptions import ErreurGenerationIndisponible
from mauricette.domaine.ports.generation_reponse import (
    ExtraitContexte,
    GenerationReponsePort,
    ReponseGeneree,
)

INSTRUCTIONS_SYSTEME = """Tu es un assistant qui aide une collectivité territoriale française à analyser \
les documents d'un Appel d'Offres d'assurance. Réponds uniquement à partir des extraits de documents \
fournis, numérotés entre crochets (ex: [1], [2]). N'invente jamais d'information absente des extraits.

Réponds strictement en JSON valide, avec ce format exact :
{"reponse": "<texte de la réponse, ou null si l'information n'est pas trouvée>", \
"score_confiance": <nombre entre 0 et 1>, "indices_extraits_utilises": [<indices entiers des extraits \
effectivement utilisés pour répondre>]}

Règles :
- "reponse" doit TOUJOURS être une simple chaîne de texte (ou null), jamais un objet ou une liste JSON \
imbriquée — même si l'information comporte plusieurs éléments (plusieurs dates, plusieurs garanties...). \
Dans ce cas, énumère-les dans le texte lui-même, séparés par des virgules ou des retours à la ligne \
(ex: "24/11/2025 : date limite de réception ; 01/01/2026 : début du marché").
- Si l'information n'est présente dans aucun extrait, "reponse" doit être null, "score_confiance" 0.0 \
et "indices_extraits_utilises" une liste vide.
- Si l'information est claire et non ambiguë, utilise un score de confiance élevé (proche de 1).
- Si l'information est partielle, ambiguë ou déduite indirectement, utilise un score de confiance faible \
(inférieur à 0.5).
- Ne cite dans "indices_extraits_utilises" que les extraits réellement utilisés pour construire la réponse."""


class MistralGenerationAdapter(GenerationReponsePort):
    """Génère des réponses aux questions du référentiel via l'API Mistral (Mistral Large)."""

    def __init__(self, parametres: Parametres) -> None:
        self._client = Mistral(api_key=parametres.mistral_api_key)
        self._modele = parametres.mistral_generation_model

    def generer_reponse(
        self,
        question: str,
        format_attendu: FormatReponse,
        aide_extraction: str | None,
        extraits: list[ExtraitContexte],
    ) -> ReponseGeneree:
        if not extraits:
            return ReponseGeneree(contenu=None, score_confiance=0.0, chunks_utilises=[])

        message_utilisateur = self._construire_message_utilisateur(
            question, format_attendu, aide_extraction, extraits
        )

        try:
            reponse_api = self._client.chat.complete(
                model=self._modele,
                messages=[
                    {"role": "system", "content": INSTRUCTIONS_SYSTEME},
                    {"role": "user", "content": message_utilisateur},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
        except MistralError as erreur:
            raise ErreurGenerationIndisponible(
                f"Le service de génération Mistral est indisponible : {erreur}"
            ) from erreur
        except Exception as erreur:  # timeout réseau, DNS, etc.
            raise ErreurGenerationIndisponible(
                f"Échec de connexion au service de génération Mistral : {erreur}"
            ) from erreur

        return self._interpreter_reponse(reponse_api.choices[0].message.content, extraits)

    @staticmethod
    def _construire_message_utilisateur(
        question: str,
        format_attendu: FormatReponse,
        aide_extraction: str | None,
        extraits: list[ExtraitContexte],
    ) -> str:
        blocs_extraits = "\n\n".join(
            f"[{i}] (document : {e.document_nom}"
            f"{f', page {e.page_debut}' if e.page_debut else ''}"
            f"{f', section : {e.titre_section}' if e.titre_section else ''})\n{e.contenu}"
            for i, e in enumerate(extraits, start=1)
        )
        aide = f"\nAide à l'extraction : {aide_extraction}" if aide_extraction else ""
        return (
            f"Question : {question}\n"
            f"Format de réponse attendu : {format_attendu.value}{aide}\n\n"
            f"Extraits disponibles :\n\n{blocs_extraits}"
        )

    @staticmethod
    def _interpreter_reponse(contenu_brut: str, extraits: list[ExtraitContexte]) -> ReponseGeneree:
        try:
            donnees = json.loads(contenu_brut)
            contenu = donnees.get("reponse")
            # Le modèle suit généralement la consigne (une chaîne), mais renvoie parfois
            # une structure JSON (liste/dict) pour des réponses naturellement composites
            # (ex: une liste de dates) : on la sérialise pour respecter le contrat "texte".
            if contenu is not None and not isinstance(contenu, str):
                contenu = json.dumps(contenu, ensure_ascii=False)
            score_confiance = float(donnees.get("score_confiance", 0.0))
            indices = donnees.get("indices_extraits_utilises", []) or []
        except (json.JSONDecodeError, TypeError, ValueError) as erreur:
            raise ErreurGenerationIndisponible(
                f"Réponse du modèle de génération illisible (JSON invalide) : {erreur}"
            ) from erreur

        chunks_utilises = [
            extraits[i - 1].chunk_id for i in indices if isinstance(i, int) and 1 <= i <= len(extraits)
        ]
        return ReponseGeneree(
            contenu=contenu,
            score_confiance=max(0.0, min(1.0, score_confiance)),
            chunks_utilises=chunks_utilises,
        )
