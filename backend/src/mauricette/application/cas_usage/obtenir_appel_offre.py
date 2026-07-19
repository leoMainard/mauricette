"""Cas d'usage : consulter un Appel d'Offres et ses documents."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.document import Document
from mauricette.domaine.exceptions import EntiteIntrouvable
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort


@dataclass(frozen=True)
class DetailAppelOffre:
    """Vue agrégée d'un Appel d'Offres et de ses documents."""

    appel_offre: AppelOffre
    documents: list[Document]


class ObtenirAppelOffre:
    """Récupère un Appel d'Offres avec la liste de ses documents déposés."""

    def __init__(
        self,
        depot_appels_offre: AppelOffreRepositoryPort,
        depot_documents: DocumentRepositoryPort,
    ) -> None:
        self._depot_appels_offre = depot_appels_offre
        self._depot_documents = depot_documents

    def executer(self, appel_offre_id: UUID) -> DetailAppelOffre:
        """Exécute le cas d'usage, lève `EntiteIntrouvable` si l'AO n'existe pas."""
        appel_offre = self._depot_appels_offre.obtenir_par_id(appel_offre_id)
        if appel_offre is None:
            raise EntiteIntrouvable(f"Appel d'Offres introuvable : {appel_offre_id}")
        documents = self._depot_documents.lister_par_appel_offre(appel_offre_id)
        return DetailAppelOffre(appel_offre=appel_offre, documents=documents)
