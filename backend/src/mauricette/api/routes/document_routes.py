"""Routes HTTP relatives au dépôt et à la consultation des documents."""

from __future__ import annotations

import posixpath
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status

from mauricette.api.dependances import (
    obtenir_cas_usage_deposer_fichier,
    obtenir_cas_usage_obtenir_contenu_document,
    obtenir_cas_usage_supprimer_document,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse
from mauricette.application.cas_usage.deposer_fichier import (
    CommandeDeposerFichier,
    DeposerFichier,
)
from mauricette.application.cas_usage.obtenir_contenu_document import (
    CommandeObtenirContenuDocument,
    ObtenirContenuDocument,
)
from mauricette.application.cas_usage.supprimer_document import (
    CommandeSupprimerDocument,
    SupprimerDocument,
)
from mauricette.domaine.exceptions import EntiteIntrouvable, ErreurDepotDocument

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}/documents", tags=["Documents"])


@routeur.post("", response_model=DepotFichierReponse, status_code=status.HTTP_201_CREATED)
async def deposer_document(
    appel_offre_id: UUID,
    fichier: UploadFile,
    cas_usage: DeposerFichier = Depends(obtenir_cas_usage_deposer_fichier),
) -> DepotFichierReponse:
    """Dépose un fichier dans l'Appel d'Offres donné.

    Si le fichier est une archive .zip valide, elle est automatiquement éclatée
    en documents individuels (le zip lui-même n'est pas conservé). Les fichiers
    dont le contenu est déjà présent dans l'AO (même hash) sont ignorés.
    """
    commande = CommandeDeposerFichier(
        appel_offre_id=appel_offre_id,
        nom_original=fichier.filename or "document_sans_nom",
        contenu=fichier.file,
        type_mime=fichier.content_type or "application/octet-stream",
    )
    try:
        resultat = cas_usage.executer(commande)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except ErreurDepotDocument as erreur:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(erreur)
        ) from erreur
    return DepotFichierReponse.depuis_resultat(resultat)


@routeur.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_document(
    appel_offre_id: UUID,
    document_id: UUID,
    cas_usage: SupprimerDocument = Depends(obtenir_cas_usage_supprimer_document),
) -> None:
    """Supprime un document (stockage et base de données)."""
    try:
        cas_usage.executer(
            CommandeSupprimerDocument(appel_offre_id=appel_offre_id, document_id=document_id)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur


@routeur.get("/{document_id}/contenu")
def obtenir_contenu_document(
    appel_offre_id: UUID,
    document_id: UUID,
    cas_usage: ObtenirContenuDocument = Depends(obtenir_cas_usage_obtenir_contenu_document),
) -> Response:
    """Retourne le contenu binaire d'un document, pour aperçu dans l'interface.

    Le fichier est proxifié depuis le stockage (local ou S3/MinIO) plutôt que
    redirigé vers une URL signée, pour éviter tout souci de CORS côté navigateur
    (parsing DOCX/XLSX en JS) et fonctionner à l'identique quel que soit
    l'adaptateur de stockage actif.
    """
    try:
        resultat = cas_usage.executer(
            CommandeObtenirContenuDocument(appel_offre_id=appel_offre_id, document_id=document_id)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur

    # Un fichier issu d'un zip éclaté peut avoir un nom_original contenant des "/" :
    # on ne garde que le nom de base. `filename*=UTF-8''...` (RFC 5987/6266) plutôt
    # que `filename="..."` : ce dernier est limité au Latin-1 et casserait sur un
    # nom accentué (application francophone).
    nom_base = posixpath.basename(resultat.nom_original.replace("\\", "/"))
    return Response(
        content=resultat.contenu,
        media_type=resultat.type_mime or "application/octet-stream",
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{quote(nom_base)}"},
    )
