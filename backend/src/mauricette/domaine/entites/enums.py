"""Énumérations métier partagées par les entités du domaine."""

from enum import StrEnum


class StatutAppelOffre(StrEnum):
    """Cycle de vie d'un Appel d'Offres, du dépôt à l'archivage."""

    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    TRAITE = "traite"
    ARCHIVE = "archive"


class StatutDocument(StrEnum):
    """Cycle de vie d'un document déposé, indépendamment de son traitement RAG."""

    EN_ATTENTE = "en_attente"
    TELEVERSE = "televerse"
    EN_ERREUR = "en_erreur"
    TRAITE = "traite"


class FournisseurStockage(StrEnum):
    """Identifie l'adaptateur de stockage utilisé pour un document donné.

    Stocké en base par document (et non en config globale) afin de pouvoir
    changer de fournisseur dans le temps sans casser l'accès aux documents
    déjà déposés.
    """

    LOCAL = "local"
    S3 = "s3"


class FormatReponse(StrEnum):
    """Type de réponse attendue pour une question du référentiel.

    Guide à la fois l'utilisateur qui rédige la question et, plus tard, le RAG
    qui devra formuler sa réponse dans le format attendu.
    """

    OUI_NON = "oui_non"
    MONTANT = "montant"
    DATE = "date"
    POURCENTAGE = "pourcentage"
    LISTE = "liste"
    TEXTE_LIBRE = "texte_libre"
    AUTRE = "autre"
