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


class StatutEtape(StrEnum):
    """Statut d'une étape du pipeline RAG (extraction, découpage, embedding)."""

    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    REUSSI = "reussi"
    ECHEC = "echec"


class TypeChunk(StrEnum):
    """Nature du contenu d'un chunk : texte courant ou tableau extrait tel quel."""

    TEXTE = "texte"
    TABLEAU = "tableau"


class TypeTache(StrEnum):
    """Type de traitement asynchrone à exécuter par le worker RAG."""

    EXTRACTION_DOCUMENT = "extraction_document"
    DECOUPAGE_DOCUMENT = "decoupage_document"
    EMBEDDING_DOCUMENT = "embedding_document"
    REGENERATION_REPONSES_AO = "regeneration_reponses_ao"


class StatutTache(StrEnum):
    """Cycle de vie d'une tâche dans la file d'attente de traitement RAG."""

    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    REUSSI = "reussi"
    ECHEC = "echec"


class StatutReponse(StrEnum):
    """Cycle de vie d'une réponse générée pour une question de référentiel."""

    GENEREE = "generee"
    VALIDEE_UTILISATEUR = "valide_utilisateur"
