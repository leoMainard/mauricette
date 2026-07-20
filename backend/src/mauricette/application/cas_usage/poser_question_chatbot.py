"""Cas d'usage : poser une question libre au chatbot d'un Appel d'Offres.

Contrairement à `RegenererReponsesAppelOffre` (questions fixes d'un référentiel,
régénérées en bloc), chaque message du chatbot est indépendant et immédiat : on
répond à une seule question, en tenant compte des derniers échanges de la
conversation pour permettre les questions de suivi.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.config.parametres import Parametres
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import FormatReponse, RoleMessageChatbot
from mauricette.domaine.entites.message_chatbot import MessageChatbot
from mauricette.domaine.entites.reponse_question import Citation
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.chunk_repository import ChunkRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.embedding import EmbeddingPort
from mauricette.domaine.ports.generation_reponse import (
    ExtraitContexte,
    GenerationReponsePort,
    TourConversation,
)
from mauricette.domaine.ports.message_chatbot_repository import MessageChatbotRepositoryPort

MESSAGE_INFORMATION_NON_TROUVEE = "Information non trouvée dans les documents."


@dataclass(frozen=True)
class CommandePoserQuestionChatbot:
    """Question posée par l'utilisateur au chatbot d'un Appel d'Offres."""

    appel_offre_id: UUID
    question: str


class PoserQuestionChatbot:
    """Répond à une question libre sur les documents d'un AO, avec citations et mémoire de conversation."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_messages: MessageChatbotRepositoryPort,
        depot_chunks: ChunkRepositoryPort,
        depot_documents: DocumentRepositoryPort,
        embedding: EmbeddingPort,
        generation: GenerationReponsePort,
        parametres: Parametres,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_messages = depot_messages
        self._depot_chunks = depot_chunks
        self._depot_documents = depot_documents
        self._embedding = embedding
        self._generation = generation
        self._nombre_chunks_recherche = parametres.rag_nombre_chunks_recherche
        self._nombre_echanges_historique = parametres.rag_chatbot_nombre_echanges_historique

    def executer(self, commande: CommandePoserQuestionChatbot) -> MessageChatbot:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(commande.appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {commande.appel_offre_id}")

        # Récupéré avant la persistance du message utilisateur courant, pour ne pas
        # se retrouver deux fois dans le contexte (une fois comme historique, une
        # fois comme question courante).
        historique = self._construire_historique(commande.appel_offre_id)

        message_utilisateur = MessageChatbot(
            appel_offre_id=commande.appel_offre_id,
            role=RoleMessageChatbot.UTILISATEUR,
            contenu=commande.question,
        )
        self._depot_messages.ajouter(message_utilisateur)

        vecteur_question = self._embedding.vectoriser_un(commande.question)
        chunks = self._depot_chunks.recherche_hybride(
            commande.appel_offre_id,
            vecteur_question,
            commande.question,
            limite=self._nombre_chunks_recherche,
        )

        if not chunks:
            message_assistant = MessageChatbot(
                appel_offre_id=commande.appel_offre_id,
                role=RoleMessageChatbot.ASSISTANT,
                contenu=None,
                score_confiance=0.0,
                citations=[],
            )
            self._depot_messages.ajouter(message_assistant)
            return message_assistant

        documents_par_id = {
            document.id: document
            for document in self._depot_documents.lister_par_appel_offre(commande.appel_offre_id)
        }
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
            commande.question,
            FormatReponse.TEXTE_LIBRE,
            None,
            extraits,
            historique=historique,
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

        message_assistant = MessageChatbot(
            appel_offre_id=commande.appel_offre_id,
            role=RoleMessageChatbot.ASSISTANT,
            contenu=resultat.contenu,
            score_confiance=resultat.score_confiance,
            citations=citations,
        )
        self._depot_messages.ajouter(message_assistant)
        return message_assistant

    def _construire_historique(self, appel_offre_id: UUID) -> list[TourConversation]:
        derniers_messages = self._depot_messages.lister_derniers(
            appel_offre_id, self._nombre_echanges_historique * 2
        )
        return [
            TourConversation(role=message.role, contenu=message.contenu or MESSAGE_INFORMATION_NON_TROUVEE)
            for message in derniers_messages
        ]

    @staticmethod
    def _nom_document(document_id: UUID, documents_par_id: dict[UUID, Document]) -> str:
        document = documents_par_id.get(document_id)
        return document.nom_original if document is not None else "Document inconnu"
