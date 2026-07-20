"""Cas d'usage : volume de documents traités par jour, tous AO confondus."""

from __future__ import annotations

from datetime import date

from mauricette.domaine.ports.document_repository import DocumentRepositoryPort


class ObtenirVolumeDocumentsParJour:
    """Retourne, pour chaque jour, le nombre de documents dont l'analyse s'est terminée."""

    def __init__(self, depot_documents: DocumentRepositoryPort) -> None:
        self._depot_documents = depot_documents

    def executer(self) -> dict[date, int]:
        return self._depot_documents.compter_traites_par_jour()
