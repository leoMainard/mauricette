"""Sérialisation du résultat d'extraction, pour le passage de relais entre les
étapes d'extraction et de découpage (stocké entre les deux comme un fichier
JSON, via `StockageDocumentPort`, plutôt que de gonfler Postgres)."""

from __future__ import annotations

import json
from uuid import UUID

from mauricette.domaine.entites.enums import TypeChunk
from mauricette.domaine.ports.extracteur_document import ElementExtrait, ResultatExtraction

TYPE_MIME_EXTRACTION = "application/json"


def serialiser_resultat_extraction(resultat: ResultatExtraction) -> bytes:
    """Convertit un `ResultatExtraction` en JSON, pour stockage intermédiaire."""
    donnees = {
        "elements": [
            {
                "type_element": element.type_element.value,
                "texte": element.texte,
                "titre_section": element.titre_section,
                "niveau_titre": element.niveau_titre,
                "page_debut": element.page_debut,
                "page_fin": element.page_fin,
            }
            for element in resultat.elements
        ]
    }
    return json.dumps(donnees).encode("utf-8")


def deserialiser_resultat_extraction(contenu: bytes) -> ResultatExtraction:
    """Reconstruit un `ResultatExtraction` à partir de son JSON sérialisé."""
    donnees = json.loads(contenu.decode("utf-8"))
    return ResultatExtraction(
        elements=[
            ElementExtrait(
                type_element=TypeChunk(element["type_element"]),
                texte=element["texte"],
                titre_section=element["titre_section"],
                niveau_titre=element["niveau_titre"],
                page_debut=element["page_debut"],
                page_fin=element["page_fin"],
            )
            for element in donnees["elements"]
        ]
    )


def cle_stockage_extraction(appel_offre_id: UUID, document_id: UUID) -> str:
    """Clé de stockage du résultat d'extraction intermédiaire d'un document."""
    return f"appels_offre/{appel_offre_id}/{document_id}/extraction.json"
