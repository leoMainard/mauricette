"""Hachage et vérification des mots de passe (bcrypt).

Isolé ici pour que les cas d'usage n'importent pas directement `bcrypt` :
seul ce module connaît l'algorithme de hachage utilisé.
"""

from __future__ import annotations

import bcrypt


def hacher(mot_de_passe: str) -> str:
    """Retourne le hash bcrypt (salé) du mot de passe en clair."""
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifier(mot_de_passe: str, mot_de_passe_hash: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond bien au hash stocké."""
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), mot_de_passe_hash.encode("utf-8"))
