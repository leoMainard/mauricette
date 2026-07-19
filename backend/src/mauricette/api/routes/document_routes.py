"""Routes HTTP relatives au dépôt et à la consultation des documents."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from mauricette.api.dependances import (
    obtenir_cas_usage_deposer_fichier,
    obtenir_cas_usage_supprimer_document,
)
from mauricette.api.schemas.document_schemas import DepotFichierReponse
from mauricette.application.cas_usage.deposer_fichier import (
    CommandeDeposerFichier,
    DeposerFichier,
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
