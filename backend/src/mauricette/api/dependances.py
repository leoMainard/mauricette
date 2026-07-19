"""Câblage des dépendances FastAPI (injection de dépendances).

C'est le seul endroit de la couche `api` qui connaît les implémentations
concrètes (SQLAlchemy, S3/local). Les routes ne dépendent que des cas d'usage,
eux-mêmes définis uniquement en fonction des ports du domaine.
"""

from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from mauricette.application.cas_usage.creer_appel_offre import CreerAppelOffre
from mauricette.application.cas_usage.deposer_document import DeposerDocument
from mauricette.application.cas_usage.deposer_fichier import DeposerFichier
from mauricette.application.cas_usage.lister_appels_offre import ListerAppelsOffre
from mauricette.application.cas_usage.modifier_appel_offre import ModifierAppelOffre
from mauricette.application.cas_usage.obtenir_appel_offre import ObtenirAppelOffre
from mauricette.application.cas_usage.supprimer_document import SupprimerDocument
from mauricette.config.parametres import obtenir_parametres
from mauricette.domaine.ports.appel_offre_repository import AppelOffreRepositoryPort
from mauricette.domaine.ports.document_repository import DocumentRepositoryPort
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.infrastructure.persistence.postgres.appel_offre_repository_sql import (
    AppelOffreRepositorySQL,
)
from mauricette.infrastructure.persistence.postgres.base import GestionnaireSessions
from mauricette.infrastructure.persistence.postgres.document_repository_sql import (
    DocumentRepositorySQL,
)
from mauricette.infrastructure.stockage.fabrique_stockage import creer_adaptateur_stockage


@lru_cache
def obtenir_gestionnaire_sessions() -> GestionnaireSessions:
    """Fournit le gestionnaire de sessions PostgreSQL, unique pour toute l'app."""
    return GestionnaireSessions(obtenir_parametres())


@lru_cache
def obtenir_stockage() -> StockageDocumentPort:
    """Fournit l'adaptateur de stockage de documents configuré (local ou S3/MinIO)."""
    return creer_adaptateur_stockage(obtenir_parametres())


def obtenir_session(
    gestionnaire: GestionnaireSessions = Depends(obtenir_gestionnaire_sessions),
) -> Iterator[Session]:
    """Fournit une session SQLAlchemy, fermée à la fin de la requête HTTP."""
    yield from gestionnaire.obtenir_session()


def obtenir_depot_appels_offre(
    session: Session = Depends(obtenir_session),
) -> AppelOffreRepositoryPort:
    """Fournit l'implémentation courante du port `AppelOffreRepositoryPort`."""
    return AppelOffreRepositorySQL(session)


def obtenir_depot_documents(
    session: Session = Depends(obtenir_session),
) -> DocumentRepositoryPort:
    """Fournit l'implémentation courante du port `DocumentRepositoryPort`."""
    return DocumentRepositorySQL(session)


def obtenir_cas_usage_creer_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
) -> CreerAppelOffre:
    """Fournit le cas d'usage de création d'Appel d'Offres, prêt à l'emploi."""
    return CreerAppelOffre(depot_appels_offre)


def obtenir_cas_usage_lister_appels_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> ListerAppelsOffre:
    """Fournit le cas d'usage de listing des Appels d'Offres, prêt à l'emploi."""
    return ListerAppelsOffre(depot_appels_offre, depot_documents)


def obtenir_cas_usage_modifier_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
) -> ModifierAppelOffre:
    """Fournit le cas d'usage de renommage d'un Appel d'Offres, prêt à l'emploi."""
    return ModifierAppelOffre(depot_appels_offre)


def obtenir_cas_usage_obtenir_appel_offre(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> ObtenirAppelOffre:
    """Fournit le cas d'usage de consultation d'un Appel d'Offres, prêt à l'emploi."""
    return ObtenirAppelOffre(depot_appels_offre, depot_documents)


def obtenir_cas_usage_deposer_document(
    depot_appels_offre: AppelOffreRepositoryPort = Depends(obtenir_depot_appels_offre),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
    stockage: StockageDocumentPort = Depends(obtenir_stockage),
) -> DeposerDocument:
    """Fournit le cas d'usage de dépôt de document, prêt à l'emploi."""
    return DeposerDocument(depot_appels_offre, depot_documents, stockage)


def obtenir_cas_usage_deposer_fichier(
    deposer_document: DeposerDocument = Depends(obtenir_cas_usage_deposer_document),
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
) -> DeposerFichier:
    """Fournit le cas d'usage de dépôt de fichier (avec éclatement zip et dédoublonnage)."""
    return DeposerFichier(deposer_document, depot_documents)


def obtenir_cas_usage_supprimer_document(
    depot_documents: DocumentRepositoryPort = Depends(obtenir_depot_documents),
    stockage: StockageDocumentPort = Depends(obtenir_stockage),
) -> SupprimerDocument:
    """Fournit le cas d'usage de suppression d'un document, prêt à l'emploi."""
    return SupprimerDocument(depot_documents, stockage)
