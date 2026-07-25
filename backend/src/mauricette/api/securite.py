"""Émission et vérification du jeton de session (JWT stocké en cookie httpOnly)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from mauricette.config.parametres import Parametres
from mauricette.domaine.exceptions import IdentifiantsInvalides

NOM_COOKIE_SESSION = "mauricette_session"
_ALGORITHME = "HS256"


def creer_jeton(utilisateur_id: UUID, parametres: Parametres) -> str:
    """Génère un JWT signé, valide pour la durée configurée, identifiant l'utilisateur."""
    expiration = datetime.now(timezone.utc) + timedelta(minutes=parametres.jwt_expiration_minutes)
    return jwt.encode(
        {"sub": str(utilisateur_id), "exp": expiration}, parametres.jwt_secret, algorithm=_ALGORITHME
    )


def decoder_jeton(jeton: str, parametres: Parametres) -> UUID:
    """Décode et valide le JWT, retourne l'id utilisateur qu'il identifie.

    Lève `IdentifiantsInvalides` si le jeton est absent, expiré, ou falsifié.
    """
    try:
        payload = jwt.decode(jeton, parametres.jwt_secret, algorithms=[_ALGORITHME])
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as erreur:
        raise IdentifiantsInvalides("Session invalide ou expirée.") from erreur
