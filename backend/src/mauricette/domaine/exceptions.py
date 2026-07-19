"""Exceptions métier du domaine, indépendantes de tout framework."""


class ErreurDomaine(Exception):
    """Classe de base pour toutes les erreurs métier de Mauricette."""


class ErreurValidationDomaine(ErreurDomaine):
    """Levée quand une entité ne respecte pas une règle métier (ex: nom vide)."""


class EntiteIntrouvable(ErreurDomaine):
    """Levée quand une entité demandée n'existe pas (ex: AO ou document inconnu)."""


class ErreurDepotDocument(ErreurDomaine):
    """Levée quand l'écriture d'un document dans le stockage échoue."""
