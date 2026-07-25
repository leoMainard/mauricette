"""Routes HTTP pour l'export du questionnaire (réponses) d'un Appel d'Offres."""

from __future__ import annotations

from typing import Literal
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from mauricette.api.dependances import obtenir_cas_usage_exporter_reponses_appel_offre
from mauricette.api.export.rendu_docx import generer_docx
from mauricette.api.export.rendu_pdf import generer_pdf
from mauricette.api.export.rendu_xlsx import generer_xlsx
from mauricette.application.cas_usage.exporter_reponses_appel_offre import (
    ExporterReponsesAppelOffre,
)
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}/reponses", tags=["Export"])

_TYPES_MIME = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@routeur.get("/export")
def exporter_reponses(
    appel_offre_id: UUID,
    format: Literal["pdf", "docx", "xlsx"],
    cas_usage: ExporterReponsesAppelOffre = Depends(obtenir_cas_usage_exporter_reponses_appel_offre),
) -> Response:
    """Exporte le questionnaire complet (questions actives + réponses) d'un AO."""
    try:
        export = cas_usage.executer(appel_offre_id)
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur

    if format == "pdf":
        contenu = generer_pdf(export)
    elif format == "docx":
        contenu = generer_docx(export)
    else:
        contenu = generer_xlsx(export)

    nom_fichier = f"{export.nom_appel_offre}.{format}"
    return Response(
        content=contenu,
        media_type=_TYPES_MIME[format],
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(nom_fichier)}"},
    )
