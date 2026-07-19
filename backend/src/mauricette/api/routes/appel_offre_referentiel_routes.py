"""Routes HTTP pour le rattachement des référentiels à un Appel d'Offres."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mauricette.api.dependances import (
    obtenir_cas_usage_attacher_referentiel,
    obtenir_cas_usage_detacher_referentiel,
    obtenir_cas_usage_lister_referentiels_ao,
)
from mauricette.api.schemas.referentiel_schemas import (
    RattachementReferentielRequete,
    ReferentielReponse,
)
from mauricette.application.cas_usage.attacher_referentiel_appel_offre import (
    AttacherReferentielAAppelOffre,
    CommandeAttacherReferentiel,
)
from mauricette.application.cas_usage.detacher_referentiel_appel_offre import (
    CommandeDetacherReferentiel,
    DetacherReferentielDeAppelOffre,
)
from mauricette.application.cas_usage.lister_referentiels_appel_offre import (
    ListerReferentielsAppelOffre,
)
from mauricette.domaine.exceptions import EntiteIntrouvable

routeur = APIRouter(prefix="/appels-offre/{appel_offre_id}/referentiels", tags=["Référentiels d'un AO"])


@routeur.get("", response_model=list[ReferentielReponse])
def lister_referentiels_de_ao(
    appel_offre_id: UUID,
    cas_usage: ListerReferentielsAppelOffre = Depends(obtenir_cas_usage_lister_referentiels_ao),
) -> list[ReferentielReponse]:
    """Liste les référentiels actuellement rattachés à un Appel d'Offres."""
    return [ReferentielReponse.depuis_entite(r) for r in cas_usage.executer(appel_offre_id)]


@routeur.post("", response_model=list[ReferentielReponse], status_code=status.HTTP_201_CREATED)
def attacher_referentiel(
    appel_offre_id: UUID,
    requete: RattachementReferentielRequete,
    cas_usage_attacher: AttacherReferentielAAppelOffre = Depends(obtenir_cas_usage_attacher_referentiel),
    cas_usage_lister: ListerReferentielsAppelOffre = Depends(obtenir_cas_usage_lister_referentiels_ao),
) -> list[ReferentielReponse]:
    """Rattache un référentiel supplémentaire à un Appel d'Offres."""
    try:
        cas_usage_attacher.executer(
            CommandeAttacherReferentiel(appel_offre_id=appel_offre_id, referentiel_id=requete.referentiel_id)
        )
    except EntiteIntrouvable as erreur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erreur)) from erreur
    return [ReferentielReponse.depuis_entite(r) for r in cas_usage_lister.executer(appel_offre_id)]


@routeur.delete("/{referentiel_id}", status_code=status.HTTP_204_NO_CONTENT)
def detacher_referentiel(
    appel_offre_id: UUID,
    referentiel_id: UUID,
    cas_usage: DetacherReferentielDeAppelOffre = Depends(obtenir_cas_usage_detacher_referentiel),
) -> None:
    """Détache un référentiel d'un Appel d'Offres."""
    cas_usage.executer(
        CommandeDetacherReferentiel(appel_offre_id=appel_offre_id, referentiel_id=referentiel_id)
    )
