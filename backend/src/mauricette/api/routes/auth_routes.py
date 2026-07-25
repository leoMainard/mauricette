"""Routes HTTP d'authentification (inscription, connexion, profil).

Contrairement à tous les autres routeurs de l'application, celui-ci n'est PAS
protégé par la dépendance d'authentification globale (voir `api/main.py`) —
c'est justement lui qui permet de s'authentifier.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from mauricette.api.dependances import (
    obtenir_cas_usage_changer_mot_de_passe,
    obtenir_cas_usage_connecter_utilisateur,
    obtenir_cas_usage_inscrire_utilisateur,
    obtenir_cas_usage_modifier_profil_utilisateur,
    obtenir_utilisateur_courant,
)
from mauricette.api.schemas.utilisateur_schemas import (
    ChangementMotDePasseRequete,
    ConnexionRequete,
    InscriptionRequete,
    ModificationProfilRequete,
    UtilisateurReponse,
)
from mauricette.api.securite import NOM_COOKIE_SESSION, creer_jeton
from mauricette.application.cas_usage.changer_mot_de_passe import (
    ChangerMotDePasse,
    CommandeChangerMotDePasse,
)
from mauricette.application.cas_usage.connecter_utilisateur import (
    CommandeConnecterUtilisateur,
    ConnecterUtilisateur,
)
from mauricette.application.cas_usage.inscrire_utilisateur import (
    CommandeInscrireUtilisateur,
    InscrireUtilisateur,
)
from mauricette.application.cas_usage.modifier_profil_utilisateur import (
    CommandeModifierProfilUtilisateur,
    ModifierProfilUtilisateur,
)
from mauricette.config.parametres import obtenir_parametres
from mauricette.domaine.entites.utilisateur import Utilisateur
from mauricette.domaine.exceptions import EmailDejaUtilise, EntiteIntrouvable, IdentifiantsInvalides

routeur = APIRouter(prefix="/auth", tags=["Authentification"])


def _poser_cookie_session(reponse: Response, utilisateur_id: UUID) -> None:
    parametres = obtenir_parametres()
    jeton = creer_jeton(utilisateur_id, parametres)
    reponse.set_cookie(
        key=NOM_COOKIE_SESSION,
        value=jeton,
        httponly=True,
        samesite="lax",
        secure=False,  # TODO: passer à True en production (HTTPS)
        max_age=parametres.jwt_expiration_minutes * 60,
    )


@routeur.post("/inscription", response_model=UtilisateurReponse, status_code=status.HTTP_201_CREATED)
def inscription(
    requete: InscriptionRequete,
    reponse: Response,
    cas_usage: InscrireUtilisateur = Depends(obtenir_cas_usage_inscrire_utilisateur),
) -> UtilisateurReponse:
    """Crée un nouveau compte utilisateur et ouvre immédiatement la session."""
    try:
        utilisateur = cas_usage.executer(
            CommandeInscrireUtilisateur(
                email=requete.email, mot_de_passe=requete.mot_de_passe, nom=requete.nom
            )
        )
    except EmailDejaUtilise as erreur:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erreur)) from erreur
    _poser_cookie_session(reponse, utilisateur.id)
    return UtilisateurReponse.depuis_entite(utilisateur)


@routeur.post("/connexion", response_model=UtilisateurReponse)
def connexion(
    requete: ConnexionRequete,
    reponse: Response,
    cas_usage: ConnecterUtilisateur = Depends(obtenir_cas_usage_connecter_utilisateur),
) -> UtilisateurReponse:
    """Vérifie les identifiants et ouvre la session."""
    try:
        utilisateur = cas_usage.executer(
            CommandeConnecterUtilisateur(email=requete.email, mot_de_passe=requete.mot_de_passe)
        )
    except IdentifiantsInvalides as erreur:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erreur)) from erreur
    _poser_cookie_session(reponse, utilisateur.id)
    return UtilisateurReponse.depuis_entite(utilisateur)


@routeur.post("/deconnexion", status_code=status.HTTP_204_NO_CONTENT)
def deconnexion(reponse: Response) -> None:
    """Ferme la session (supprime le cookie)."""
    reponse.delete_cookie(key=NOM_COOKIE_SESSION)


@routeur.get("/moi", response_model=UtilisateurReponse)
def moi(utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant)) -> UtilisateurReponse:
    """Retourne l'utilisateur actuellement connecté (hydratation de session côté frontend)."""
    return UtilisateurReponse.depuis_entite(utilisateur)


@routeur.patch("/profil", response_model=UtilisateurReponse)
def modifier_profil(
    requete: ModificationProfilRequete,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
    cas_usage: ModifierProfilUtilisateur = Depends(obtenir_cas_usage_modifier_profil_utilisateur),
) -> UtilisateurReponse:
    """Modifie le nom et l'email de l'utilisateur connecté."""
    try:
        modifie = cas_usage.executer(
            CommandeModifierProfilUtilisateur(
                utilisateur_id=utilisateur.id, nom=requete.nom, email=requete.email
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except EmailDejaUtilise as erreur:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erreur)) from erreur
    return UtilisateurReponse.depuis_entite(modifie)


@routeur.patch("/mot-de-passe", status_code=status.HTTP_204_NO_CONTENT)
def changer_mot_de_passe(
    requete: ChangementMotDePasseRequete,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
    cas_usage: ChangerMotDePasse = Depends(obtenir_cas_usage_changer_mot_de_passe),
) -> None:
    """Change le mot de passe de l'utilisateur connecté."""
    try:
        cas_usage.executer(
            CommandeChangerMotDePasse(
                utilisateur_id=utilisateur.id,
                ancien_mot_de_passe=requete.ancien_mot_de_passe,
                nouveau_mot_de_passe=requete.nouveau_mot_de_passe,
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    except IdentifiantsInvalides as erreur:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erreur)) from erreur
