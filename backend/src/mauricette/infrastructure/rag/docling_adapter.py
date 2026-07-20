"""Adaptateur d'extraction de documents basé sur Docling."""

from __future__ import annotations

import os

# Docling télécharge ses modèles depuis Hugging Face Hub au premier lancement.
# Le cache Hugging Face utilise des liens symboliques par défaut, ce qui échoue
# sur Windows sans le Mode développeur activé (ou des droits administrateur) :
# on désactive ce mécanisme pour que le téléchargement fonctionne partout.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from io import BytesIO  # noqa: E402
from pathlib import Path  # noqa: E402

from docling.document_converter import DocumentConverter  # noqa: E402
from docling_core.types.doc import DocItemLabel
from docling_core.types.doc.document import TableItem, TextItem
from docling_core.types.io import DocumentStream

from mauricette.domaine.entites.enums import TypeChunk
from mauricette.domaine.exceptions import ErreurExtractionDocument
from mauricette.domaine.ports.extracteur_document import (
    ElementExtrait,
    ExtracteurDocumentPort,
    ResultatExtraction,
)

# Extensions vérifiées avant tout appel à Docling : évite une conversion longue
# et vouée à l'échec sur un format manifestement non supporté. Docling gère en
# réalité une liste bien plus large (audio, vidéo, XML scientifiques...), sans
# intérêt pour des documents d'Appel d'Offres : on ne retient ici que les
# formats plausibles pour ce contexte (bureautique, web, texte, images scannées).
EXTENSIONS_SUPPORTEES = {
    ".pdf",
    ".docx", ".dotx", ".docm", ".dotm",
    ".xlsx", ".xlsm",
    ".pptx", ".potx", ".ppsx", ".pptm", ".potm", ".ppsm",
    ".odt", ".ott", ".ods", ".ots", ".odp", ".otp",
    ".html", ".htm", ".xhtml",
    ".md", ".txt", ".text",
    ".csv",
    ".epub",
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp",
}

# Titres/sections : ces labels marquent une nouvelle position dans la hiérarchie
# du document, utilisée pour construire le fil d'ariane (`titre_section`).
LABELS_TITRE = {DocItemLabel.SECTION_HEADER, DocItemLabel.TITLE}

# Labels de texte courant à conserver comme contenu (le reste : images, formulaires,
# pieds de page... est ignoré, non pertinent pour la recherche RAG).
LABELS_TEXTE = {
    DocItemLabel.TEXT,
    DocItemLabel.PARAGRAPH,
    DocItemLabel.LIST_ITEM,
    DocItemLabel.CAPTION,
    DocItemLabel.CODE,
    DocItemLabel.FORMULA,
}


class DoclingAdapter(ExtracteurDocumentPort):
    """Extrait le contenu structuré d'un document via la bibliothèque Docling."""

    def __init__(self) -> None:
        self._convertisseur = DocumentConverter()

    def extraire(self, contenu: bytes, nom_fichier: str, type_mime: str) -> ResultatExtraction:
        extension = Path(nom_fichier).suffix.lower()
        if extension not in EXTENSIONS_SUPPORTEES:
            raise ErreurExtractionDocument(f"Format non supporté : {extension or 'inconnu'}.")

        flux = DocumentStream(name=nom_fichier, stream=BytesIO(contenu))
        try:
            resultat = self._convertisseur.convert(flux)
        except Exception as erreur:
            raise ErreurExtractionDocument(self._traduire_erreur(erreur)) from erreur

        document = resultat.document
        elements: list[ElementExtrait] = []
        titre_par_niveau: dict[int, str] = {}

        for item, niveau in document.iterate_items():
            if isinstance(item, TableItem):
                page = item.prov[0].page_no if item.prov else None
                elements.append(
                    ElementExtrait(
                        type_element=TypeChunk.TABLEAU,
                        texte=item.export_to_markdown(document),
                        titre_section=self._chemin_titre(titre_par_niveau),
                        niveau_titre=None,
                        page_debut=page,
                        page_fin=page,
                    )
                )
                continue

            if not isinstance(item, TextItem) or not item.text or not item.text.strip():
                continue

            page = item.prov[0].page_no if item.prov else None

            if item.label in LABELS_TITRE:
                titre_par_niveau = {n: t for n, t in titre_par_niveau.items() if n < niveau}
                titre_par_niveau[niveau] = item.text
                elements.append(
                    ElementExtrait(
                        type_element=TypeChunk.TEXTE,
                        texte=item.text,
                        titre_section=self._chemin_titre(titre_par_niveau),
                        niveau_titre=niveau,
                        page_debut=page,
                        page_fin=page,
                    )
                )
            elif item.label in LABELS_TEXTE:
                elements.append(
                    ElementExtrait(
                        type_element=TypeChunk.TEXTE,
                        texte=item.text,
                        titre_section=self._chemin_titre(titre_par_niveau),
                        niveau_titre=None,
                        page_debut=page,
                        page_fin=page,
                    )
                )

        return ResultatExtraction(elements=elements)

    @staticmethod
    def _chemin_titre(titre_par_niveau: dict[int, str]) -> str | None:
        if not titre_par_niveau:
            return None
        return " > ".join(titre_par_niveau[niveau] for niveau in sorted(titre_par_niveau))

    @staticmethod
    def _traduire_erreur(erreur: Exception) -> str:
        message = str(erreur).lower()
        if "password" in message or "encrypt" in message:
            return "Le document est protégé par un mot de passe."
        if "unsupported" in message or "format" in message:
            return "Format de document non supporté ou fichier corrompu."
        return f"Échec de l'extraction du document : {erreur}"
