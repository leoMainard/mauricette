"""Port (interface) pour la persistance des Documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from mauricette.domaine.entites.document import Document


@dataclass(frozen=True)
class StatistiquesDocuments:
    """Agrégat (nombre de documents, taille cumulée) pour un Appel d'Offres."""

    nombre_documents: int
    taille_totale_octets: int


class DocumentRepositoryPort(ABC):
    """Contrat que doit respecter tout adaptateur de persistance des documents."""

    @abstractmethod
    def ajouter(self, document: Document) -> None:
        """Persiste un nouveau document."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_id(self, document_id: UUID) -> Document | None:
        """Retourne le document correspondant à l'identifiant, ou None."""
        raise NotImplementedError

    @abstractmethod
    def lister_par_appel_offre(self, appel_offre_id: UUID) -> list[Document]:
        """Retourne tous les documents rattachés à un Appel d'Offres."""
        raise NotImplementedError

    @abstractmethod
    def mettre_a_jour(self, document: Document) -> None:
        """Enregistre les modifications apportées à un document existant."""
        raise NotImplementedError

    @abstractmethod
    def obtenir_par_hash(self, appel_offre_id: UUID, hash_sha256: str) -> Document | None:
        """Retourne un document existant du même AO ayant le même contenu (même hash), si présent.

        Utilisé pour détecter les doublons avant d'écrire un nouveau document.
        """
        raise NotImplementedError

    @abstractmethod
    def supprimer(self, document_id: UUID) -> None:
        """Supprime définitivement l'enregistrement d'un document."""
        raise NotImplementedError

    @abstractmethod
    def compter_par_appel_offre(self) -> dict[UUID, StatistiquesDocuments]:
        """Retourne, pour chaque AO ayant au moins un document, ses statistiques.

        Une seule requête agrégée (plutôt qu'un comptage par AO) pour éviter le
        problème des N+1 requêtes lors de l'affichage de la liste des AO.
        """
        raise NotImplementedError

    @abstractmethod
    def compter_traites_par_jour(self) -> dict[date, int]:
        """Retourne, pour chaque jour, le nombre de documents dont le traitement RAG
        s'est terminé avec succès ce jour-là.

        Granularité journalière (plutôt qu'hebdomadaire) pour permettre au frontend de
        reconstituer lui-même des vues jour/semaine/mois par regroupement. S'appuie
        sur `date_maj` des documents au statut `traite` : cette date n'est plus
        modifiée une fois ce statut atteint (aucune autre mutation ne s'applique à un
        document déjà traité), donc c'est une date de complétion fiable. Une seule
        requête agrégée pour tout l'historique, pas de N+1.
        """
        raise NotImplementedError
