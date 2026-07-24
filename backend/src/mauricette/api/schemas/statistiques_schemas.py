"""Schémas Pydantic (contrats HTTP) pour les statistiques globales du tableau de bord."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class VolumeJourReponse(BaseModel):
    """Nombre de documents traités durant un jour donné."""

    jour: date
    nombre: int
