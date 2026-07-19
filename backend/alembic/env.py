"""Environnement Alembic : branche les migrations sur la configuration Mauricette.

L'URL de connexion n'est jamais dupliquée dans `alembic.ini` : elle est lue
depuis `Parametres` (donc depuis le `.env`), comme partout ailleurs dans le projet.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from mauricette.config.parametres import obtenir_parametres
from mauricette.infrastructure.persistence.postgres.base import Base, creer_moteur

# Importer les modèles pour qu'ils s'enregistrent sur `Base.metadata`.
from mauricette.infrastructure.persistence.postgres import modeles  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

parametres = obtenir_parametres()


def run_migrations_offline() -> None:
    """Génère le SQL des migrations sans se connecter à la base (mode 'offline')."""
    context.configure(
        url=parametres.url_base_donnees,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Applique les migrations via une connexion réelle à la base (mode 'online')."""
    moteur = creer_moteur(parametres)

    with moteur.connect() as connexion:
        _configurer_et_migrer(connexion)

    moteur.dispose()


def _configurer_et_migrer(connexion: Connection) -> None:
    context.configure(connection=connexion, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
