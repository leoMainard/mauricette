"""Fabrique qui sélectionne l'adaptateur de stockage selon la configuration.

C'est le seul endroit du code qui décide "quel fournisseur de stockage utiliser".
Pour ajouter un nouveau fournisseur (ex: Cloudflare R2 avec des identifiants
distincts, Backblaze B2...), il suffit d'ajouter un cas ici et un adaptateur
implémentant `StockageDocumentPort`.
"""

from mauricette.config.parametres import Parametres
from mauricette.domaine.ports.stockage_document import StockageDocumentPort
from mauricette.infrastructure.stockage.stockage_local import StockageLocal
from mauricette.infrastructure.stockage.stockage_s3 import StockageS3


def creer_adaptateur_stockage(parametres: Parametres) -> StockageDocumentPort:
    """Instancie l'adaptateur de stockage correspondant à `parametres.storage_provider`."""
    if parametres.storage_provider == "s3":
        return StockageS3(
            endpoint_url=parametres.s3_endpoint_url,
            access_key=parametres.s3_access_key,
            secret_key=parametres.s3_secret_key,
            bucket_name=parametres.s3_bucket_name,
            region=parametres.s3_region,
            use_ssl=parametres.s3_use_ssl,
        )
    if parametres.storage_provider == "local":
        return StockageLocal(dossier_racine=parametres.stockage_local_dossier)

    raise ValueError(f"Fournisseur de stockage inconnu : {parametres.storage_provider}")
