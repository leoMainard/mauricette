"""Adaptateurs de stockage binaire des documents (local ou S3/MinIO)."""

from mauricette.infrastructure.stockage.fabrique_stockage import creer_adaptateur_stockage
from mauricette.infrastructure.stockage.stockage_local import StockageLocal
from mauricette.infrastructure.stockage.stockage_s3 import StockageS3

__all__ = ["StockageLocal", "StockageS3", "creer_adaptateur_stockage"]
