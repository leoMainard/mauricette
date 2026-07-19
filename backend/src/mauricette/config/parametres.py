"""Chargement typé de la configuration applicative depuis le fichier .env.

Ce module est le seul endroit du projet où l'on lit des variables d'environnement.
Le reste du code reçoit ses paramètres via l'objet `Parametres`, ce qui permet de
tester chaque composant avec des valeurs arbitraires sans dépendre de l'environnement.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Racine du dépôt (deux niveaux au-dessus de backend/), où vit le fichier .env partagé.
RACINE_DEPOT = Path(__file__).resolve().parents[4]


class Parametres(BaseSettings):
    """Paramètres de configuration de Mauricette, chargés depuis `.env`."""

    model_config = SettingsConfigDict(
        env_file=RACINE_DEPOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Base de données PostgreSQL ---
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "mauricette"
    db_user: str = "postgres"
    db_password: str = ""

    # --- Stockage documents ---
    storage_provider: str = "local"  # "local" ou "s3"
    stockage_local_dossier: Path = RACINE_DEPOT / "storage_local"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket_name: str = "mauricette-documents"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False

    # --- API ---
    api_cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def url_base_donnees(self) -> str:
        """Construit l'URL de connexion SQLAlchemy (driver psycopg v3)."""
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def obtenir_parametres() -> Parametres:
    """Retourne l'instance unique (mise en cache) des paramètres applicatifs."""
    return Parametres()
