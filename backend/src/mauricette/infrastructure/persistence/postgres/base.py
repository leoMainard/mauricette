"""Base technique SQLAlchemy : moteur, fabrique de sessions, classe déclarative.

Point d'entrée unique pour toute connexion PostgreSQL. Si demain la base change
de moteur (ex: passage à un autre SGBD compatible SQLAlchemy), seul ce fichier
et les modèles ORM associés sont à adapter.
"""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from mauricette.config.parametres import Parametres


class Base(DeclarativeBase):
    """Classe de base déclarative pour tous les modèles ORM de Mauricette."""


def creer_moteur(parametres: Parametres) -> Engine:
    """Crée le moteur SQLAlchemy à partir des paramètres de connexion."""
    return create_engine(parametres.url_base_donnees, pool_pre_ping=True)


def creer_fabrique_sessions(moteur: Engine) -> sessionmaker[Session]:
    """Crée la fabrique de sessions liée au moteur donné."""
    return sessionmaker(bind=moteur, autoflush=False, expire_on_commit=False)


class GestionnaireSessions:
    """Fournit des sessions SQLAlchemy et centralise leur cycle de vie.

    Utilisé comme dépendance FastAPI : une session par requête HTTP,
    fermée automatiquement à la fin de la requête.
    """

    def __init__(self, parametres: Parametres) -> None:
        self._moteur = creer_moteur(parametres)
        self._fabrique_sessions = creer_fabrique_sessions(self._moteur)

    @property
    def moteur(self) -> Engine:
        """Moteur SQLAlchemy sous-jacent (utile pour Alembic ou les tests)."""
        return self._moteur

    def obtenir_session(self) -> Iterator[Session]:
        """Générateur de session, à utiliser avec `Depends` côté FastAPI."""
        session = self._fabrique_sessions()
        try:
            yield session
        finally:
            session.close()
