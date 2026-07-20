"""Adaptateur de découpage en chunks, respectant la structure du document.

Le texte est regroupé sous un même fil d'ariane de titres jusqu'à atteindre une
taille cible, avec un léger chevauchement entre chunks consécutifs pour ne pas
perdre le contexte à la frontière. Les tableaux ne sont jamais fusionnés avec
du texte : chacun devient son propre chunk.
"""

from __future__ import annotations

from uuid import UUID

from mauricette.config.parametres import Parametres
from mauricette.domaine.entites.chunk import Chunk
from mauricette.domaine.entites.enums import TypeChunk
from mauricette.domaine.ports.decoupeur_document import DecoupeurDocumentPort
from mauricette.domaine.ports.extracteur_document import ElementExtrait, ResultatExtraction


class DecoupeurHierarchique(DecoupeurDocumentPort):
    """Découpe un résultat d'extraction en chunks structurés par section."""

    def __init__(self, parametres: Parametres) -> None:
        self._taille_cible = parametres.rag_taille_cible_chunk_caracteres
        self._chevauchement = parametres.rag_chevauchement_chunk_caracteres

    def decouper(
        self, document_id: UUID, appel_offre_id: UUID, resultat_extraction: ResultatExtraction
    ) -> list[Chunk]:
        chunks: list[Chunk] = []
        ordre = 0

        tampon = ""
        titre_tampon: str | None = None
        page_debut_tampon: int | None = None
        page_fin_tampon: int | None = None

        def vider_tampon() -> None:
            nonlocal tampon, titre_tampon, page_debut_tampon, page_fin_tampon, ordre
            if tampon.strip():
                chunks.append(
                    Chunk(
                        document_id=document_id,
                        appel_offre_id=appel_offre_id,
                        contenu=tampon.strip(),
                        type_chunk=TypeChunk.TEXTE,
                        page_debut=page_debut_tampon,
                        page_fin=page_fin_tampon,
                        titre_section=titre_tampon,
                        ordre=ordre,
                    )
                )
                ordre += 1
            tampon = ""
            titre_tampon = None
            page_debut_tampon = None
            page_fin_tampon = None

        for element in resultat_extraction.elements:
            if element.type_element == TypeChunk.TABLEAU:
                vider_tampon()
                chunks.append(
                    Chunk(
                        document_id=document_id,
                        appel_offre_id=appel_offre_id,
                        contenu=element.texte.strip(),
                        type_chunk=TypeChunk.TABLEAU,
                        page_debut=element.page_debut,
                        page_fin=element.page_fin,
                        titre_section=element.titre_section,
                        ordre=ordre,
                    )
                )
                ordre += 1
                continue

            if titre_tampon is None:
                titre_tampon = element.titre_section
            if page_debut_tampon is None:
                page_debut_tampon = element.page_debut
            page_fin_tampon = element.page_fin or page_fin_tampon

            if tampon and len(tampon) + len(element.texte) > self._taille_cible:
                chevauchement_texte = tampon[-self._chevauchement :] if self._chevauchement > 0 else ""
                vider_tampon()
                tampon = chevauchement_texte
                titre_tampon = element.titre_section
                page_debut_tampon = element.page_debut
                page_fin_tampon = element.page_fin

            tampon = f"{tampon}\n\n{element.texte}" if tampon else element.texte

        vider_tampon()
        return chunks
