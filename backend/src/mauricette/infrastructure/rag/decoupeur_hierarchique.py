"""Adaptateur de découpage en chunks, respectant la structure du document.

Le texte est regroupé sous un même fil d'ariane de titres jusqu'à atteindre une
taille cible, avec un léger chevauchement entre chunks consécutifs pour ne pas
perdre le contexte à la frontière. Les tableaux ne sont jamais fusionnés avec
du texte, mais un tableau trop volumineux (ex: un tableur exporté en un seul
bloc markdown) est lui-même redécoupé par lignes pour rester sous la taille
cible : un tableau non découpé peut dépasser la limite de tokens acceptée par
le modèle d'embedding, ce qui ferait échouer le traitement à chaque tentative,
y compris après relance.
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
                for contenu_tableau in self._decouper_tableau(element.texte):
                    chunks.append(
                        Chunk(
                            document_id=document_id,
                            appel_offre_id=appel_offre_id,
                            contenu=contenu_tableau,
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

    def _decouper_tableau(self, texte_tableau: str) -> list[str]:
        """Redécoupe un tableau markdown trop volumineux en plusieurs chunks par lignes.

        Les deux premières lignes (en-têtes de colonnes + ligne de séparation
        markdown) sont répétées dans chaque morceau, pour que chaque chunk reste
        un tableau lisible et interprétable isolément (important pour la
        recherche/génération), plutôt que des lignes de données sans contexte.
        """
        texte_tableau = texte_tableau.strip()
        lignes = texte_tableau.split("\n")

        if len(texte_tableau) <= self._taille_cible or len(lignes) <= 2:
            return [texte_tableau]

        entete = lignes[:2]
        # Les tableaux markdown alignent chaque colonne sur sa cellule la plus
        # large : l'en-tête peut donc à lui seul peser plusieurs milliers de
        # caractères. On part son poids en compte dès le départ, sans quoi le
        # budget de taille ne reflèterait que les lignes de données et
        # sous-estimerait la taille réelle de chaque morceau.
        taille_entete = len("\n".join(entete))
        morceaux: list[str] = []
        lignes_tampon: list[str] = []
        taille_tampon = taille_entete

        def vider_tampon_tableau() -> None:
            if lignes_tampon:
                morceaux.append("\n".join(entete + lignes_tampon))

        for ligne in lignes[2:]:
            if lignes_tampon and taille_tampon + len(ligne) > self._taille_cible:
                vider_tampon_tableau()
                lignes_tampon = []
                taille_tampon = taille_entete
            lignes_tampon.append(ligne)
            taille_tampon += len(ligne) + 1

        vider_tampon_tableau()
        return morceaux
