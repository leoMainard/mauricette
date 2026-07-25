"""Exceptions métier du domaine, indépendantes de tout framework."""


class ErreurDomaine(Exception):
    """Classe de base pour toutes les erreurs métier de Mauricette."""


class ErreurValidationDomaine(ErreurDomaine):
    """Levée quand une entité ne respecte pas une règle métier (ex: nom vide)."""


class EntiteIntrouvable(ErreurDomaine):
    """Levée quand une entité demandée n'existe pas (ex: AO ou document inconnu)."""


class IdentifiantsInvalides(ErreurDomaine):
    """Levée quand l'email ou le mot de passe fourni ne correspond à aucun compte."""


class EmailDejaUtilise(ErreurDomaine):
    """Levée quand l'email demandé (inscription ou changement) est déjà pris par un autre compte."""


class ErreurDepotDocument(ErreurDomaine):
    """Levée quand l'écriture d'un document dans le stockage échoue."""


class ErreurTraitementTransitoire(ErreurDomaine):
    """Erreur probablement temporaire (quota API, timeout réseau) : à re-tenter automatiquement."""


class ErreurTraitementDefinitive(ErreurDomaine):
    """Erreur qui ne se résoudra pas en re-tentant (format non supporté, mot de passe requis...)."""


class ErreurExtractionDocument(ErreurTraitementDefinitive):
    """Levée quand l'extraction du contenu d'un document échoue durablement."""


class ErreurEmbeddingIndisponible(ErreurTraitementTransitoire):
    """Levée quand le fournisseur d'embedding est temporairement indisponible (quota, timeout)."""


class ErreurGenerationIndisponible(ErreurTraitementTransitoire):
    """Levée quand le fournisseur de génération est temporairement indisponible (quota, timeout)."""


class ErreurEtatTraitementInvalide(ErreurDomaine):
    """Levée par RelancerDocument si le document ciblé n'est pas en échec de traitement RAG."""
