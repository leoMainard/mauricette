"""Cas d'usage : régénération complète des réponses aux questions de référentiel d'un AO.

Toujours une régénération intégrale (jamais un patch incrémental) : les anciennes
réponses sont remplacées en bloc une fois toutes les nouvelles calculées, jamais
question par question — un crash en cours de route laisse donc les réponses
précédentes intactes plutôt que la moitié effacées.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.config.parametres import Parametres
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import StatutAppelOffre
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.reponse_question import Citation, ReponseQuestion
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.embedding import EmbeddingPort
from mauricette.domaine.ports.generation_reponse import ExtraitContexte, GenerationReponsePort
from mauricette.domaine.ports.question_referentiel_repository import (
    QuestionReferentielRepositoryPort,
)
from mauricette.domaine.ports.referentiel_appel_offre_repository import (
    ReferentielAppelOffreRepositoryPort,
)
from mauricette.domaine.ports.reponse_question_repository import ReponseQuestionRepositoryPort


@dataclass(frozen=True)
class CommandeRegenererReponsesAppelOffre:
    """Identifie l'Appel d'Offres dont il faut régénérer toutes les réponses."""

    appel_offre_id: UUID


class RegenererReponsesAppelOffre:
    """Recalcule, pour un AO, la réponse à chaque question active des référentiels attachés."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_referentiels_ao: ReferentielAppelOffreRepositoryPort,
        depot_questions: QuestionReferentielRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        depot_chunks: ChunkRepositoryPort,
        depot_reponses: ReponseQuestionRepositoryPort,
        embedding: EmbeddingPort,
        generation: GenerationReponsePort,
        parametres: Parametres,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_referentiels_ao = depot_referentiels_ao
        self._depot_questions = depot_questions
        self._depot_documents = depot_documents
        self._depot_chunks = depot_chunks
        self._depot_reponses = depot_reponses
        self._embedding = embedding
        self._generation = generation
        self._nombre_chunks_recherche = parametres.rag_nombre_chunks_recherche

    def executer(self, commande: CommandeRegenererReponsesAppelOffre) -> None:
        appel_offre_id = commande.appel_offre_id

        referentiels = self._depot_referentiels_ao.lister_referentiels_pour_ao(appel_offre_id)
        questions_actives = [
            question
            for referentiel in referentiels
            for question in self._depot_questions.lister_par_referentiel(referentiel.id)
            if question.actif
        ]

        documents_par_id = {
            document.id: document
            for document in self._depot_documents.lister_par_appel_offre(appel_offre_id)
        }

        nouvelles_reponses = [
            self._repondre_a_une_question(appel_offre_id, question, documents_par_id)
            for question in questions_actives
        ]

        self._depot_reponses.remplacer_pour_appel_offre(appel_offre_id, nouvelles_reponses)

        # La régénération est la dernière étape du pipeline RAG : une fois les réponses
        # calculées, l'AO est considéré comme traité (transition douce, jamais de retour
        # en arrière automatique si l'AO a déjà été archivé ou traité manuellement).
        appel_offre = self._depot_appels_offre.obtenir_par_id(appel_offre_id)
        if appel_offre is not None and appel_offre.statut == StatutAppelOffre.EN_COURS:
            appel_offre.marquer_traite()
            self._depot_appels_offre.mettre_a_jour(appel_offre)

    def _repondre_a_une_question(
        self,
        appel_offre_id: UUID,
        question: QuestionReferentiel,
        documents_par_id: dict[UUID, Document],
    ) -> ReponseQuestion:
        texte_requete = question.aide_extraction or question.question
        vecteur_question = self._embedding.vectoriser_un(texte_requete)
        chunks = self._depot_chunks.recherche_hybride(
            appel_offre_id, vecteur_question, texte_requete, limite=self._nombre_chunks_recherche
        )

        if not chunks:
            return ReponseQuestion(
                appel_offre_id=appel_offre_id,
                question_referentiel_id=question.id,
                contenu=None,
                score_confiance=0.0,
                citations=[],
            )

        chunks_par_id = {chunk.id: chunk for chunk in chunks}
        extraits = [
            ExtraitContexte(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_nom=self._nom_document(chunk.document_id, documents_par_id),
                page_debut=chunk.page_debut,
                page_fin=chunk.page_fin,
                titre_section=chunk.titre_section,
                contenu=chunk.contenu,
            )
            for chunk in chunks
        ]

        resultat = self._generation.generer_reponse(
            question.question, question.format_reponse, question.aide_extraction, extraits
        )

        citations = [
            Citation(
                chunk_id=chunk_id,
                document_id=chunks_par_id[chunk_id].document_id,
                document_nom=self._nom_document(chunks_par_id[chunk_id].document_id, documents_par_id),
                page_debut=chunks_par_id[chunk_id].page_debut,
                page_fin=chunks_par_id[chunk_id].page_fin,
                titre_section=chunks_par_id[chunk_id].titre_section,
            )
            for chunk_id in resultat.chunks_utilises
            if chunk_id in chunks_par_id
        ]

        return ReponseQuestion(
            appel_offre_id=appel_offre_id,
            question_referentiel_id=question.id,
            contenu=resultat.contenu,
            score_confiance=resultat.score_confiance,
            citations=citations,
        )

    @staticmethod
    def _nom_document(document_id: UUID, documents_par_id: dict[UUID, Document]) -> str:
        document = documents_par_id.get(document_id)
        return document.nom_original if document is not None else "Document inconnu"
