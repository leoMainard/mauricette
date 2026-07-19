"""Adaptateur de stockage compatible API S3 (MinIO, Cloudflare R2, AWS S3...).

Cet adaptateur ne dépend que de l'API S3 standard via `boto3` : il fonctionne
sans modification avec MinIO en local, ou avec n'importe quel fournisseur
compatible S3 en changeant simplement l'URL d'`endpoint` en configuration.
"""

from __future__ import annotations

from typing import BinaryIO

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from mauricette.domaine.entites.enums import FournisseurStockage
from mauricette.domaine.ports.stockage_document import StockageDocumentPort


class StockageS3(StockageDocumentPort):
    """Stocke les documents sur un service compatible API S3 (ex: MinIO)."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1",
        use_ssl: bool = False,
    ) -> None:
        self._bucket_name = bucket_name
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=use_ssl,
            config=BotoConfig(signature_version="s3v4"),
        )
        self._creer_bucket_si_absent()

    @property
    def fournisseur(self) -> FournisseurStockage:
        return FournisseurStockage.S3

    def enregistrer(self, cle: str, contenu: BinaryIO, type_mime: str) -> None:
        self._client.upload_fileobj(
            contenu, self._bucket_name, cle, ExtraArgs={"ContentType": type_mime}
        )

    def recuperer(self, cle: str) -> bytes:
        reponse = self._client.get_object(Bucket=self._bucket_name, Key=cle)
        return reponse["Body"].read()

    def supprimer(self, cle: str) -> None:
        self._client.delete_object(Bucket=self._bucket_name, Key=cle)

    def generer_url_temporaire(self, cle: str, expiration_secondes: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name, "Key": cle},
            ExpiresIn=expiration_secondes,
        )

    def _creer_bucket_si_absent(self) -> None:
        """Crée le bucket cible s'il n'existe pas encore (confort en développement)."""
        try:
            self._client.head_bucket(Bucket=self._bucket_name)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket_name)
