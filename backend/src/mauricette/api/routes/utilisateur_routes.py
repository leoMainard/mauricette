"""Routes HTTP d'administration : groupes d'utilisateurs et affectation des membres.

Toutes les routes de ce routeur exigent le statut ADMIN (voir `dependencies=`
sur l'`APIRouter` ci-dessous).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_affecter_groupe_utilisateur,
    obtenir_cas_usage_creer_groupe_utilisateur,
    obtenir_cas_usage_lister_groupes_utilisateur,
    obtenir_cas_usage_lister_utilisateurs,
    obtenir_utilisateur_admin,
)
from mauricette.api.schemas.utilisateur_schemas import (
    AffectationGroupeRequete,
    CreationGroupeRequete,
    GroupeUtilisateurReponse,
    UtilisateurReponse,
)
from mauricette.application.cas_usage.affecter_groupe_utilisateur import (
    AffecterGroupeUtilisateur,
    CommandeAffecterGroupeUtilisateur,
)
from mauricette.application.cas_usage.creer_groupe_utilisateur import (
    CommandeCreerGroupeUtilisateur,
    CreerGroupeUtilisateur,
)
from mauricette.application.cas_usage.lister_groupes_utilisateur import ListerGroupesUtilisateur
from mauricette.application.cas_usage.lister_utilisateurs import ListerUtilisateurs
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(
    tags=["Administration"],
    dependencies=[Depends(obtenir_utilisateur_admin)],
)


@routeur.post("/groupes", response_model=GroupeUtilisateurReponse, status_code=status.HTTP_201_CREATED)
def creer_groupe(
    requete: CreationGroupeRequete,
    cas_usage: CreerGroupeUtilisateur = Depends(obtenir_cas_usage_creer_groupe_utilisateur),
) -> GroupeUtilisateurReponse:
    """Crée un nouveau groupe d'utilisateurs."""
    groupe = cas_usage.executer(CommandeCreerGroupeUtilisateur(nom=requete.nom))
    return GroupeUtilisateurReponse.depuis_entite(groupe)


@routeur.get("/groupes", response_model=list[GroupeUtilisateurReponse])
def lister_groupes(
    cas_usage: ListerGroupesUtilisateur = Depends(obtenir_cas_usage_lister_groupes_utilisateur),
) -> list[GroupeUtilisateurReponse]:
    """Liste tous les groupes d'utilisateurs."""
    return [GroupeUtilisateurReponse.depuis_entite(g) for g in cas_usage.executer()]


@routeur.get("/utilisateurs", response_model=list[UtilisateurReponse])
def lister_utilisateurs(
    cas_usage: ListerUtilisateurs = Depends(obtenir_cas_usage_lister_utilisateurs),
) -> list[UtilisateurReponse]:
    """Liste tous les utilisateurs."""
    return [UtilisateurReponse.depuis_entite(u) for u in cas_usage.executer()]


@routeur.patch("/utilisateurs/{utilisateur_id}/groupe", response_model=UtilisateurReponse)
def affecter_groupe(
    utilisateur_id: UUID,
    requete: AffectationGroupeRequete,
    cas_usage: AffecterGroupeUtilisateur = Depends(obtenir_cas_usage_affecter_groupe_utilisateur),
) -> UtilisateurReponse:
    """Affecte un utilisateur à un groupe (ou l'en retire si `groupe_id` est `null`)."""
    try:
        utilisateur = cas_usage.executer(
            CommandeAffecterGroupeUtilisateur(
                utilisateur_id=utilisateur_id, groupe_id=requete.groupe_id
            )
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return UtilisateurReponse.depuis_entite(utilisateur)
