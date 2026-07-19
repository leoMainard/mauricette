"""Conversion entre modèles ORM (SQLAlchemy) et entités du domaine.

Isoler ce mapping ici évite de polluer le domaine avec des détails de
persistance, et évite de polluer les modèles ORM avec de la logique métier.
"""

from mauricette.domaine.entites.appel_offre import AppelOffre
from mauricette.domaine.entites.document import Document
from mauricette.domaine.entites.enums import FormatReponse, FournisseurStockage, StatutAppelOffre, StatutDocument
from mauricette.domaine.entites.question_referentiel import QuestionReferentiel
from mauricette.domaine.entites.referentiel import Referentiel
from mauricette.domaine.entites.section_referentiel import SectionReferentiel
from mauricette.infrastructure.persistence.postgres.modeles import (
    AppelOffreModele,
    DocumentModele,
    QuestionReferentielModele,
    ReferentielModele,
    SectionReferentielModele,
)


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


def referentiel_vers_entite(modele: ReferentielModele) -> Referentiel:
    """Convertit un modèle ORM `ReferentielModele` en entité de domaine `Referentiel`."""
    return Referentiel(
        id=modele.id,
        nom=modele.nom,
        description=modele.description,
        actif_par_defaut=modele.actif_par_defaut,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def referentiel_vers_modele(entite: Referentiel) -> ReferentielModele:
    """Convertit une entité de domaine `Referentiel` en modèle ORM `ReferentielModele`."""
    return ReferentielModele(
        id=entite.id,
        nom=entite.nom,
        description=entite.description,
        actif_par_defaut=entite.actif_par_defaut,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )


def section_referentiel_vers_entite(modele: SectionReferentielModele) -> SectionReferentiel:
    """Convertit un modèle ORM `SectionReferentielModele` en entité de domaine."""
    return SectionReferentiel(
        id=modele.id,
        referentiel_id=modele.referentiel_id,
        nom=modele.nom,
        ordre=modele.ordre,
        date_creation=modele.date_creation,
    )


def section_referentiel_vers_modele(entite: SectionReferentiel) -> SectionReferentielModele:
    """Convertit une entité de domaine `SectionReferentiel` en modèle ORM."""
    return SectionReferentielModele(
        id=entite.id,
        referentiel_id=entite.referentiel_id,
        nom=entite.nom,
        ordre=entite.ordre,
        date_creation=entite.date_creation,
    )


def question_referentiel_vers_entite(modele: QuestionReferentielModele) -> QuestionReferentiel:
    """Convertit un modèle ORM `QuestionReferentielModele` en entité de domaine."""
    return QuestionReferentiel(
        id=modele.id,
        section_id=modele.section_id,
        question=modele.question,
        format_reponse=FormatReponse(modele.format_reponse),
        aide_extraction=modele.aide_extraction,
        obligatoire=modele.obligatoire,
        actif=modele.actif,
        ordre=modele.ordre,
        date_creation=modele.date_creation,
        date_maj=modele.date_maj,
    )


def question_referentiel_vers_modele(entite: QuestionReferentiel) -> QuestionReferentielModele:
    """Convertit une entité de domaine `QuestionReferentiel` en modèle ORM."""
    return QuestionReferentielModele(
        id=entite.id,
        section_id=entite.section_id,
        question=entite.question,
        format_reponse=entite.format_reponse.value,
        aide_extraction=entite.aide_extraction,
        obligatoire=entite.obligatoire,
        actif=entite.actif,
        ordre=entite.ordre,
        date_creation=entite.date_creation,
        date_maj=entite.date_maj,
    )
