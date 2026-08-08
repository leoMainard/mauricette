"""Schémas Pydantic (contrats HTTP) pour les Appels d'Offres.

Ces schémas ne sont volontairement pas les entités du domaine : ils décrivent
le format de la requête/réponse HTTP et peuvent évoluer indépendamment du
modèle métier (ex: masquer un champ, en agréger d'autres).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from mauricette.api.schemas.document_schemas import DocumentReponse
from mauricette.application.cas_usage.lister_appels_offre import AppelOffreAvecStatistiques
from mauricette.application.cas_usage.obtenir_appel_offre import DetailAppelOffre
from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.enums import StatutAppelOffre


class CreationAppelOffreRequete(BaseModel):
    """Corps de requête pour la création d'un Appel d'Offres.

    `cree_par`/`cree_par_id` ne sont pas fournis par le client : ils sont déduits
    de l'utilisateur authentifié par la route.
    """

    nom: str = Field(min_length=1, max_length=255, description="Nom donné à l'Appel d'Offres")


class ModificationAppelOffreRequete(BaseModel):
    """Corps de requête pour le renommage d'un Appel d'Offres."""

    nom: str = Field(min_length=1, max_length=255, description="Nouveau nom de l'Appel d'Offres")


class AppelOffreReponse(BaseModel):
    """Représentation HTTP d'un Appel d'Offres."""

    id: UUID
    nom: str
    cree_par: str
    cree_par_id: UUID | None
    statut: StatutAppelOffre
    date_creation: datetime
    date_maj: datetime

    @classmethod
    def depuis_entite(cls, appel_offre: AppelOffre) -> "AppelOffreReponse":
        """Construit le schéma de réponse à partir de l'entité de domaine."""
        return cls(
            id=appel_offre.id,
            nom=appel_offre.nom,
            cree_par=appel_offre.cree_par,
            cree_par_id=appel_offre.cree_par_id,
            statut=appel_offre.statut,
            date_creation=appel_offre.date_creation,
            date_maj=appel_offre.date_maj,
        )


class AppelOffreAvecStatistiquesReponse(BaseModel):
    """Représentation HTTP d'un Appel d'Offres enrichi de ses statistiques de documents."""

    appel_offre: AppelOffreReponse
    nombre_documents: int
    taille_totale_octets: int
    en_erreur_analyse: bool
    questions_actives: int
    reponses_generees: int

    @classmethod
    def depuis_dto(cls, dto: AppelOffreAvecStatistiques) -> "AppelOffreAvecStatistiquesReponse":
        """Construit le schéma de réponse à partir du DTO d'application `AppelOffreAvecStatistiques`."""
        return cls(
            appel_offre=AppelOffreReponse.depuis_entite(dto.appel_offre),
            nombre_documents=dto.statistiques.nombre_documents,
            taille_totale_octets=dto.statistiques.taille_totale_octets,
            en_erreur_analyse=dto.en_erreur_analyse,
            questions_actives=dto.questions_actives,
            reponses_generees=dto.reponses_generees,
        )


class AppelOffreDetailReponse(BaseModel):
    """Représentation HTTP d'un Appel d'Offres avec la liste de ses documents."""

    appel_offre: AppelOffreReponse
    documents: list[DocumentReponse]

    @classmethod
    def depuis_detail(cls, detail: DetailAppelOffre) -> "AppelOffreDetailReponse":
        """Construit le schéma de réponse à partir du DTO d'application `DetailAppelOffre`."""
        return cls(
            appel_offre=AppelOffreReponse.depuis_entite(detail.appel_offre),
            documents=[DocumentReponse.depuis_entite(document) for document in detail.documents],
        )
