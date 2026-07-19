"""Conversion entre modèles ORM (SQLAlchemy) et entités du domaine.

Isoler ce mapping ici évite de polluer le domaine avec des détails de
persistance, et évite de polluer les modèles ORM avec de la logique métier.
"""

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import FournisseurStockage, StatutAppelOffre, StatutDocument
from mauricette.infrastructure.persistence.postgres.modeles import AppelOffreModele, DocumentModele


def appel_offre_vers_entite(modele: AppelOffreModele) -> AppelOffre:
    """Convertit un modèle ORM `AppelOffreModele` en entité de domaine `AppelOffre`."""
    return AppelOffre(
        id=modele.id,
        nom=modele.nom,
        cree_par=modele.cree_par,
        statut=StatutAppelOffre(modele.statut),
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def appel_offre_vers_modele(entite: AppelOffre) -> AppelOffreModele:
    """Convertit une entité de domaine `AppelOffre` en modèle ORM `AppelOffreModele`."""
    return AppelOffreModele(
        id=entite.id,
        nom=entite.nom,
        cree_par=entite.cree_par,
        statut=entite.statut.value,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def document_vers_entite(modele: DocumentModele) -> Document:
    """Convertit un modèle ORM `DocumentModele` en entité de domaine `Document`."""
    return Document(
        id=modele.id,
        appel_offre_id=modele.appel_offre_id,
        nom_original=modele.nom_original,
        cle_stockage=modele.cle_stockage,
        fournisseur_stockage=FournisseurStockage(modele.fournisseur_stockage),
        type_mime=modele.type_mime,
        taille_octets=modele.taille_octets,
        hash_sha256=modele.hash_sha256,
        statut=StatutDocument(modele.statut),
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def document_vers_modele(entite: Document) -> DocumentModele:
    """Convertit une entité de domaine `Document` en modèle ORM `DocumentModele`."""
    return DocumentModele(
        id=entite.id,
        appel_offre_id=entite.appel_offre_id,
        nom_original=entite.nom_original,
        cle_stockage=entite.cle_stockage,
        fournisseur_stockage=entite.fournisseur_stockage.value,
        type_mime=entite.type_mime,
        taille_octets=entite.taille_octets,
        hash_sha256=entite.hash_sha256,
        statut=entite.statut.value,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )
